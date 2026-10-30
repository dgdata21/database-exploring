# ============================================================
# SECTION 1. FILE NAME
# ============================================================
# inspect_db.py

# ============================================================
# SECTION 2. IMPORTS
# ============================================================
from datetime import datetime
import pandas as pd
from sqlalchemy import text
from dotenv import load_dotenv
import ig_roadmap.db_explore.inspect_db_core as core
import ig_roadmap.db_explore.inspect_db_vars as v


# ============================================================
# SECTION 3. MAIN
# ============================================================
def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    load_dotenv(v.CREDS_PATH)

    # ==================================================
    # EXPLORE CLICKHOUSE
    # ==================================================
    start_time = datetime.now()

    client = core.connect_ch()
    tables = client.query_df(v.click_house_bases)

    print()
    print(" CLICKHOUSE OVERVIEW ".center(100, "*"))
    for db, grp in tables.groupby("database"):
        print(f"\n▸ {db} ({len(grp)} tables)")
        print(grp.drop(columns="database").to_string(index=False))

    print("\n", f"CH Connection time {datetime.now() - start_time}\n")

    # ==================================================
    # EXPLORE POSTGRESQL
    # ==================================================
    start_time = datetime.now()

    engine = core.connect_pg()

    print("\n", " POSTGRESQL OVERVIEW ".center(100, "*"), "\n")

    with engine.connect() as conn:
        tables = pd.read_sql(text(v.postgresql_bases), conn)

    print(tables.to_string(index=False))
    print("\n", f"PGSQL Connection time {datetime.now() - start_time}\n")


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
