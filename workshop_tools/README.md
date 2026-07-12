# Workshop tools

All workshop-authored Python code lives in this package. The `data/` directory
contains data files and caches only.

## Main modules

- `loader.py` — CUC corpus loader and bundled-data readers.
- `udb_loader.py` — readers for participant-built UDB Parquet tables.
- `workshop_helpers.py` — plotting and teaching helpers used across notebooks.
- `divine_networks.py` — high-level, provenance-preserving API for the Baal
  Cycle divine-name network lab.
- `similarity_helpers.py` — helpers for the similarity/clustering lab.
- `analyse.py` — metadata normalization and legacy statistical utilities.
- `build_*.py` — command-line builders for local or derived resources.
- `vendor/vis-network/` — pinned browser renderer for the draggable graph,
  bundled with its MIT licence so the lab does not depend on a CDN.

The package contains no UDB PDF, extracted text, or generated database.

## Local UDB parser exercise

## Setup (both builders)

1. Obtain the source PDF through a source you are authorized to access.
2. Save it as `local_data/Ugaritic_data_bank.pdf`.
3. Install the workshop requirements.

In Colab, both `/content/local_data/Ugaritic_data_bank.pdf` and
`/content/ugarit-dh-workshop/local_data/Ugaritic_data_bank.pdf` are detected
automatically. Set `UDB_PDF_PATH` for another location.

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
`workshop_tools/udb_loader.py` (e.g. `load_udb_texts()`, `udb_lines()`, `udb_genre_counts()`).

Both outputs are ignored by Git. Keep the PDF and all generated data local; do
not upload, commit, or redistribute them without separate authorization.

The parser performs no network download. Its synthetic regression tests do not
contain passages from the UDB publication.

## Code provenance

The parser was adapted from the private UDB conversion project maintained by
Oleksandr Sosnovshchenko. Repository-authored Python code may be reused under
the MIT option stated in the workshop repository's root `LICENSE`.
