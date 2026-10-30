# `db_explore` Package: Database Exploration

## Purpose and Overview

The first step of any project: exploring unfamiliar ClickHouse or PostgreSQL databases. This package identifies the databases, schemas, tables, and columns present, and retrieves sample rows to help you construct SQL queries for data extraction. It performs no modifications to the databases; it only executes `SELECT` statements against system catalogs and fetches a few sample rows from the tables.

## Modules

| Module | Role |
|---|---|
| `inspect_db_vars.py` | Configuration (credentials file, output directory, filters) and SQL queries |
| `inspect_db_core.py` | Helper utilities and table-viewing functions |
| `inspect_db.py` | Overview: lists all tables, including their parent databases and (for ClickHouse) their sizes |
| `inspect_db_tables.py` | Detailed view: displays sample rows and schemas for each table |

To run from the source project, use: `python Inspect_db.py` (for an overview) or `python Inspect_db_tables.py` (for table details).

## Credentials

Credentials are read from the environment, which is populated via `load_dotenv` using the file specified by `CREDS_PATH`:

| Database | Variables |
|---|---|
| ClickHouse | `cl_host`, `cl_port`, `cl_base`, `cl_user`, `cl_pass` |
| PostgreSQL | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` |

If any variable is missing, `get_cfg` will raise a `ValueError` listing the missing items. **Never** commit the file containing your passwords. ## 1. Inspect_db_vars.py

**SECTION 1. SETTINGS**
- `CREDS_PATH` — path to the file containing credentials.
- `OUT_DIR` — directory for CSV sample files (created if it does not exist).
- `CH_DATABASES` — ClickHouse databases to inspect (`None` means all).
- `PG_PREFIXES` — PostgreSQL table name prefixes (`None` means all).

**SECTION 2. QUERIES**
- `click_house_bases` — all ClickHouse tables, including their engine, row count, and size (from `system.tables`; system databases are excluded; case-insensitive due to `lower`).
- `postgresql_bases` — all PostgreSQL tables and views (from `information_schema.tables`), including object type.
- `click_house_tables` — list of tables to inspect: same as above, but excluding `.inner_id.*` system tables (internal tables used by materialized views).
- `postgres_tables` — list of tables to inspect from `pg_tables` (tables only, excluding views).
- `schema_clickhouse` — column information from `system.columns`: name, type, inclusion in the sort key or primary key, and comments. Parameters `{db}` and `{tbl}` are injected server-side.
- `schema_postgres` — column information from the `pg_attribute` catalog: name, type (including length/precision), and nullability. Uses parameters `:schema` and `:tbl`.

## 2. Inspect_db_core.py

**SECTION 1. CONNECTIONS**
- `get_cfg(keys, name)` — collects environment configuration values ​​into a dictionary; raises a `ValueError` if any required keys are missing. - `connect_ch()` — ClickHouse client (`clickhouse_connect`); the port is cast to the appropriate type.
- `connect_pg()` — SQLAlchemy engine using the `psycopg` driver (version 3); connection timeout set to 10 seconds.

**SECTION 2. CLICKHOUSE TABLES — `table_view_ch(client, Databases=None, n=15)`**
- Retrieves a list of tables; if `Databases` are specified, only the relevant databases are kept.
- For each table, it reads `n` rows, saves them to `OUT_DIR/ch_<database>.<table>.csv`, retrieves the schema, and prints both a sample and the schema.

**SECTION 3. POSTGRES TABLES — `table_view_pg(engine, Schemas=None, prefixes=None, n=15)`**
- Uses a single connection for the entire inspection process.
- Supports filtering by schemas and table name prefixes.
- For each table: retrieves a sample of `n` rows, saves to `OUT_DIR/pg_<schema>.<table>.csv`, retrieves the schema, and prints the results.

## 3. Inspect_db.py

`main()`: configures pandas output settings and loads credentials. For ClickHouse, it processes tables by database; for PostgreSQL, it lists tables and views. The time taken for each inspection block (including connection and query execution) is printed.

## 4. Inspect_db_tables.py

`main()`: configures output settings, loads credentials, and inspects all ClickHouse (`CH_DATABASES`) and PostgreSQL (`PG_PREFIXES`) tables using the `core` functions.

## Fixes

1. `inspect_db_core.py` previously imported the configuration module `inspect_vars`; this has been updated to `inspect_db_vars`. 2. `inspect_db_tables.py` previously imported `inspect_core`, which has now been renamed to `inspect_db_core`.
3. `CREDS_PATH` and `OUT_DIR` have been refactored into `vars`; table prefixes, previously hardcoded, have been moved to configuration settings (defaulting to "None").
4. In `inspect_db.py`, `load_dotenv` has been removed, and timestamp labels have been renamed.
5. In `get_cfg`, a generator variable has been renamed to avoid a naming conflict with the configuration module itself.
6. All sections have been standardized; the "FILE NAME" block has been replaced with a docstring.

## Observations

1. When inspecting ClickHouse, internal system tables (e.g., `.inner_id.*`) appear, whereas the table-listing function skips them. For PostgreSQL, the inspection includes both tables and views, while the table-listing function is restricted to tables only.
2. Unlike the ClickHouse output, the PostgreSQL inspection does not include row counts or table sizes. These could be retrieved from `pg_class` (using `reltuples` and `pg_total_relation_size`).
3. Environment variable names differ between the two databases (see the table above).
4. CSV files containing data samples may include actual, sensitive data; these should be stored outside the repository.
