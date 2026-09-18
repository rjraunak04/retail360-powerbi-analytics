# Raw Data Profiling

Retail360 profiles the downloaded AdventureWorksDW source files before PostgreSQL ingestion.

## Source-file characteristics

The official AdventureWorksDW install script bulk-loads the source files using a pipe (`|`) field terminator and UTF-8 encoding. The raw files do not use a conventional header row, so column names will be applied later from the documented warehouse schema.

## Initial profiling checks

The raw profiler validates:

- file size
- row count
- dominant field count per record
- malformed records with a different field count
- blank field occurrences
- exact duplicate source rows

These checks are intentionally performed before database loading so source-quality problems are separated from SQL transformation problems.

## Run

```powershell
python .\scripts\profile_raw_files.py
```

The script writes the summary to:

`docs/data-model/raw-data-profile.csv`

## Interpretation

- `malformed_rows = 0` means the file has a consistent record width.
- `exact_duplicate_rows` is a raw-record check only; it does not replace primary-key or grain validation.
- blank fields are not automatically errors because some warehouse attributes are nullable.

Primary-key, foreign-key and grain validation will be performed after the source columns are mapped to their documented table schemas.
