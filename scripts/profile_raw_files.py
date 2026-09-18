from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def profile_file(path: Path, delimiter: str = "|") -> dict[str, object]:
    row_count = 0
    field_count_histogram: Counter[int] = Counter()
    blank_field_count = 0
    exact_duplicate_rows = 0
    seen_rows: set[tuple[str, ...]] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for row in reader:
            if not row:
                continue

            # AdventureWorksDW source files may end records with a trailing |.
            if row and row[-1] == "":
                row = row[:-1]

            row_count += 1
            field_count_histogram[len(row)] += 1
            blank_field_count += sum(1 for value in row if value == "")

            row_tuple = tuple(row)
            if row_tuple in seen_rows:
                exact_duplicate_rows += 1
            else:
                seen_rows.add(row_tuple)

    if row_count == 0:
        expected_field_count = 0
        malformed_rows = 0
    else:
        expected_field_count = field_count_histogram.most_common(1)[0][0]
        malformed_rows = row_count - field_count_histogram[expected_field_count]

    return {
        "table": path.stem,
        "file": path.name,
        "bytes": path.stat().st_size,
        "rows": row_count,
        "expected_fields": expected_field_count,
        "malformed_rows": malformed_rows,
        "blank_fields": blank_field_count,
        "exact_duplicate_rows": exact_duplicate_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile Retail360 raw AdventureWorksDW files.")
    parser.add_argument(
        "--input",
        default="data/raw/adventureworks",
        help="Directory containing downloaded AdventureWorksDW source files.",
    )
    parser.add_argument(
        "--output",
        default="docs/data-model/raw-data-profile.csv",
        help="CSV summary written by the profiler.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_path = Path(args.output)

    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise SystemExit(f"No CSV files found in: {input_dir}")

    profiles = [profile_file(path) for path in files]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "table",
        "file",
        "bytes",
        "rows",
        "expected_fields",
        "malformed_rows",
        "blank_fields",
        "exact_duplicate_rows",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(profiles)

    print("\nRetail360 raw data profile")
    print("-" * 78)
    print(f"{'Table':30} {'Rows':>10} {'Fields':>8} {'BadRows':>9} {'DupRows':>9}")
    print("-" * 78)
    for item in profiles:
        print(
            f"{str(item['table']):30} "
            f"{int(item['rows']):>10,} "
            f"{int(item['expected_fields']):>8} "
            f"{int(item['malformed_rows']):>9,} "
            f"{int(item['exact_duplicate_rows']):>9,}"
        )
    print("-" * 78)
    print(f"Profile written to: {output_path}")


if __name__ == "__main__":
    main()
