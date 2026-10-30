# ============================================================
# SECTION 1. FILE NAME
# ============================================================
# inspect_db_tables.py

# ============================================================
# SECTION 2. IMPORTS
# ============================================================
import pandas as pd
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

    # ClickHouse: all databases unless v.CH_DATABASES is set
    client = core.connect_ch()
    core.table_view_ch(client, databases=v.CH_DATABASES)

    # Postgres: all tables unless v.PG_PREFIXES is set
    engine = core.connect_pg()
    core.table_view_pg(engine, prefixes=v.PG_PREFIXES)


if __name__ == "__main__":
    main()
    print()
