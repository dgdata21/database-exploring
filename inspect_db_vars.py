# ============================================================
# SECTION 1. FILE NAME
# ============================================================
# inspect_db_vars.py

# ============================================================
# SECTION 2. IMPORTS
# ============================================================
from pathlib import Path

# ============================================================
# SECTION 3. SETTINGS
# ============================================================
CREDS_PATH = r"/Your_Path/.creds"
OUT_DIR = Path(r"/Your_Path")

# Filters for the tables view (None - all)
CH_DATABASES = None  # e.g. ["igaming"]
PG_PREFIXES = None  # e.g. ("fact_", "dim_")

# ============================================================
# SECTION 4. QUERIES
# ============================================================
click_house_bases = """
        SELECT database, 
               name AS table,
               engine,
               total_rows AS rows,
               formatReadableSize(total_bytes) AS size
        FROM system.tables
        WHERE lower(database) NOT IN ('system', 'information_schema')
        ORDER BY database, name
"""

postgresql_bases = """
    SELECT
        table_schema AS schema,
        table_name,
        table_type
    FROM information_schema.tables
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY table_schema, table_name
"""

click_house_tables = """
        SELECT database, name
        FROM system.tables
        WHERE lower(database) NOT IN ('system', 'information_schema')
          AND name NOT LIKE '.inner_id.%'
        ORDER BY database, name
"""

postgres_tables = """
            SELECT schemaname, tablename
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename
"""

schema_clickhouse = """
    SELECT name, type,
           is_in_sorting_key AS sort_key,
           is_in_primary_key AS pk,
           comment
    FROM system.columns
    WHERE database = {db:String} AND table = {tbl:String}
    ORDER BY position
"""

schema_postgres = """
    SELECT a.attname AS name,
           format_type(a.atttypid, a.atttypmod) AS type,
           NOT a.attnotnull AS nullable
    FROM pg_attribute a
    JOIN pg_class c     ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = :schema
      AND c.relname = :tbl
      AND a.attnum > 0 AND NOT a.attisdropped
    ORDER BY a.attnum
"""
