from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

from validate_source_integrity import SCHEMAS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw" / "adventureworks"
BASE_URL = (
    "https://raw.githubusercontent.com/microsoft/sql-server-samples/master/"
    "samples/databases/adventure-works/data-warehouse-install-script"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Retail360 AdventureWorksDW source files.")
    parser.add_argument("--force", action="store_true", help="Redownload existing files.")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0

    for table in SCHEMAS:
        file_name = f"{table}.csv"
        destination = OUTPUT_DIR / file_name

        if destination.exists() and destination.stat().st_size > 0 and not args.force:
            print(f"Already exists: {file_name} ({destination.stat().st_size:,} bytes)")
            total += 1
            continue

        url = f"{BASE_URL}/{file_name}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Retail360-PowerBI-Analytics"},
        )

        print(f"Downloading: {file_name}")
        with urllib.request.urlopen(request, timeout=120) as response:
            destination.write_bytes(response.read())

        if destination.stat().st_size == 0:
            destination.unlink(missing_ok=True)
            raise RuntimeError(f"Downloaded empty file: {file_name}")

        print(f"OK: {file_name} ({destination.stat().st_size:,} bytes)")
        total += 1

    print(f"\nSource download complete: {total} files.")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
