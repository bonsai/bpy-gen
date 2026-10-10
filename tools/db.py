#!/usr/bin/env python3
"""bpy-gen generation ledger — SQLite db at ~/.db/bpy_gen.db

Tables:
  generations — script lineage (parent_id = evolutionary parent)
  renders     — render outputs linked to a generation
"""
import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path.home() / ".db" / "bpy_gen.db"


def init():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS generations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            script_name TEXT    NOT NULL,
            version     INTEGER NOT NULL DEFAULT 1,
            content_hash TEXT   NOT NULL,
            created_at  TEXT    NOT NULL,
            prompt      TEXT,
            parent_id   INTEGER REFERENCES generations(id),
            git_commit  TEXT,
            file_path   TEXT    NOT NULL,
            UNIQUE(script_name, version)
        );
        CREATE TABLE IF NOT EXISTS renders (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            generation_id INTEGER NOT NULL REFERENCES generations(id),
            output_path   TEXT    NOT NULL,
            timestamp     TEXT    NOT NULL,
            status        TEXT    DEFAULT 'ok',
            engine        TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_gen_name ON generations(script_name);
        CREATE INDEX IF NOT EXISTS idx_gen_parent ON generations(parent_id);
        """)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def bake(script_path: Path, prompt: str | None = None, parent_id: int | None = None):
    init()
    name = script_path.stem.replace("_bpy", "")
    content_hash = _hash(script_path)
    ts = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        # detect if same hash already exists
        row = conn.execute(
            "SELECT id, version FROM generations WHERE script_name=? AND content_hash=?",
            (name, content_hash),
        ).fetchone()
        if row:
            return row[0], row[1]  # existing id, version

        max_v = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM generations WHERE script_name=?",
            (name,),
        ).fetchone()[0]
        version = max_v + 1

        cur = conn.execute(
            """INSERT INTO generations(script_name, version, content_hash, created_at,
                                        prompt, parent_id, git_commit, file_path)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                name,
                version,
                content_hash,
                ts,
                prompt,
                parent_id,
                _git_commit(),
                str(script_path),
            ),
        )
        conn.commit()
        return cur.lastrowid, version


def log_render(generation_id: int, output_path: Path, engine: str = "WORKBENCH"):
    init()
    ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO renders(generation_id, output_path, timestamp, engine) VALUES (?,?,?,?)",
            (generation_id, str(output_path), ts, engine),
        )
        conn.commit()


def list_generations(script_name: str | None = None):
    init()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if script_name:
            rows = conn.execute(
                "SELECT * FROM generations WHERE script_name=? ORDER BY version",
                (script_name,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM generations ORDER BY script_name, version"
            ).fetchall()
        return [dict(r) for r in rows]


def tree(script_name: str):
    """Return generational tree as nested dict."""
    gens = list_generations(script_name)
    by_id = {g["id"]: g for g in gens}
    roots = [g for g in gens if g["parent_id"] is None]

    def _children(pid):
        return [_attach(c) for c in gens if c["parent_id"] == pid]

    def _attach(g):
        node = dict(g)
        node["children"] = _children(g["id"])
        return node

    return [_attach(r) for r in roots]


def _git_commit() -> str | None:
    import subprocess
    try:
        return (
            subprocess.check_output(
                ["git", "-C", str(Path(__file__).parent.parent), "rev-parse", "--short", "HEAD"]
            )
            .decode()
            .strip()
        )
    except Exception:
        return None


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "init"
    if cmd == "init":
        init()
        print(f"DB ready: {DB_PATH}")
    elif cmd == "bake":
        path = Path(sys.argv[2])
        gid, ver = bake(path)
        print(f"Baked: {path.stem} v{ver} (gen_id={gid})")
    elif cmd == "list":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        for g in list_generations(name):
            print(f"  {g['script_name']:20s} v{g['version']:3d}  {g['content_hash']}  {g['created_at']}")
    elif cmd == "log_render":
        # usage: db.py log_render <generation_id> <output_path> [engine]
        gen_id = int(sys.argv[2])
        out = Path(sys.argv[3])
        engine = sys.argv[4] if len(sys.argv) > 4 else "WORKBENCH"
        log_render(gen_id, out, engine)
        print(f"Logged render: gen_id={gen_id} -> {out}")
    elif cmd == "tree":
        import json as _json
        print(_json.dumps(tree(sys.argv[2]), indent=2, ensure_ascii=False, default=str))
