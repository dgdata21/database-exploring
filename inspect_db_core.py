# ============================================================
# SECTION 1. FILE NAME
# ============================================================
# inspect_db_core.py

# ============================================================
# SECTION 2. IMPORTS
# ============================================================
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import clickhouse_connect as chc
import database_exploring.inspect_db_vars as v


# ==================================================
# SECTION 3. CONNECTIONS
# ==================================================
def get_cfg(keys, name):
    cfg = {k: os.getenv(k) for k in keys}
    if missing := [k for k, v in cfg.items() if not v]:
        raise ValueError(f"Missing {name} creds: {missing}")
    return cfg


def connect_ch():
    cfg = get_cfg(
        ("cl_host", "cl_port", "cl_base", "cl_user", "cl_pass"), "ClickHouse"
    )
    return chc.get_client(
        host=cfg["cl_host"],
        port=int(cfg["cl_port"]),
        database=cfg["cl_base"],
        username=cfg["cl_user"],
        password=cfg["cl_pass"],
    )


def connect_pg():
    cfg = get_cfg(
        ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASS"), "PostgreSQL"
    )
    return create_engine(
        URL.create(
            drivername="postgresql+psycopg",
            host=cfg["DB_HOST"],
            port=int(cfg["DB_PORT"]),
            database=cfg["DB_NAME"],
            username=cfg["DB_USER"],
            password=cfg["DB_PASS"],
        ),
        connect_args={"connect_timeout": 10},
    )


# ==================================================
# SECTION 4. CLICKHOUSE TABLES
# ==================================================
def table_view_ch(client, databases=None, n=15):
    v.OUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = client.query_df(v.click_house_tables)
    if databases:
        tables = tables[tables["database"].isin(databases)]

    for database, table_name in tables.itertuples(index=False, name=None):
        df = client.query_df(
            f"SELECT * FROM `{database}`.`{table_name}` LIMIT {n}"
        )
        df.to_csv(v.OUT_DIR / f"ch_{database}.{table_name}.csv", index=False)

        schema = client.query_df(
            v.schema_clickhouse, parameters={"db": database, "tbl": table_name}
        )

        print("\n", f" {database}.{table_name} ".center(100, "="), "\n")
        print("Empty table" if df.empty else df.to_string(index=False))
        print("\n", f" {database}.{table_name} SCHEMA ".center(60, "-"), "\n")
        print(schema.to_string(index=False))


# ==================================================
# SECTION 5. POSTGRES TABLES
# ==================================================
def table_view_pg(engine, schemas=None, prefixes=None, n=15):
    v.OUT_DIR.mkdir(parents=True, exist_ok=True)

    with engine.connect() as conn:  # одно подключение на весь просмотр
        tables = pd.read_sql(text(v.postgres_tables), conn)

        if schemas:
            tables = tables[tables["schemaname"].isin(schemas)]
        if prefixes:
            tables = tables[
                tables["tablename"].str.startswith(tuple(prefixes))
            ]

        for schema, table_name in tables.itertuples(index=False, name=None):
            df = pd.read_sql(
                text(f'SELECT * FROM "{schema}"."{table_name}" LIMIT {n}'),
                conn,
            )
            df.to_csv(v.OUT_DIR / f"pg_{schema}.{table_name}.csv", index=False)

            schema_df = pd.read_sql(
                text(v.schema_postgres),
                conn,
                params={"schema": schema, "tbl": table_name},
            )

            print("\n", f" {schema}.{table_name} ".center(100, "="), "\n")
            print("Empty table" if df.empty else df.to_string(index=False))
            print(
                "\n", f" {schema}.{table_name} SCHEMA ".center(60, "-"), "\n"
            )
            print(schema_df.to_string(index=False))
