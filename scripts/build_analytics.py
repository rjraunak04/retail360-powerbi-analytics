from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql" / "analytics"

load_dotenv(ROOT / ".env")


def settings() -> dict[str, object]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD") or None,
        "dbname": os.getenv("PGDATABASE", "retail360"),
    }


def main() -> None:
    files = sorted(SQL_DIR.glob("*.sql"))
    if not files:
        raise SystemExit(f"No analytics SQL files found in {SQL_DIR}")

    with psycopg.connect(**settings()) as conn:
        for path in files:
            print(f"Applying: {path.relative_to(ROOT)}")
            conn.execute(path.read_text(encoding="utf-8"))
        conn.commit()

    print(f"Analytics star schema built successfully ({len(files)} SQL files).")


if __name__ == "__main__":
    main()
