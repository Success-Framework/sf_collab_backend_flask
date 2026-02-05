import glob
import sqlite3
import os

paths = glob.glob("instance/*.db")

print("Found DBs:", paths)

for p in paths:
    print("\n==>", p, f"({os.path.getsize(p)} bytes)")

    conn = sqlite3.connect(p)
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )

    tables = [r[0] for r in cur.fetchall()]
    print("tables:", tables if tables else "(none)")

    conn.close()
