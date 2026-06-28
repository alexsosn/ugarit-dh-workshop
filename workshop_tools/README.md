# Local UDB parser exercise

This folder contains parser, SQLite-builder, and Parquet-builder code only. It
contains no UDB PDF, extracted text, or generated database.

## Setup (both builders)

1. Obtain the source PDF through a source you are authorized to access.
2. Save it as `local_data/Ugaritic_data_bank.pdf`.
3. Install the workshop requirements.

## SQLite (Hour 3 — PDF → queryable database)

```bash
python -m workshop_tools.build_udb_sqlite --overwrite
```

Generates `local_data/udb.sqlite`.

## Parquet (earlier lessons — UDB as a tabular corpus)

```bash
python -m workshop_tools.build_udb_parquet
```

Generates five tables under `local_data/udb/` (`texts`, `readings`, `sources`,
`literature`, `tablet_comments`). The earlier-lesson notebooks read these via
`data/udb_loader.py` (e.g. `load_udb_texts()`, `udb_lines()`, `udb_genre_counts()`).

Both outputs are ignored by Git. Keep the PDF and all generated data local; do
not upload, commit, or redistribute them without separate authorization.

The parser performs no network download. Its synthetic regression tests do not
contain passages from the UDB publication.

## Code provenance

The parser was adapted from the private UDB conversion project maintained by
Oleksandr Sosnovshchenko. Repository-authored Python code may be reused under
the MIT option stated in the workshop repository's root `LICENSE`.

