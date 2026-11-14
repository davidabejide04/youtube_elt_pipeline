"""Load step: write raw rows into Snowflake."""
import logging
from pathlib import Path

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

log = logging.getLogger(__name__)
DDL_PATH = Path(__file__).resolve().parents[2] / "sql" / "create_raw_tables.sql"


def connect(params: dict):
    return snowflake.connector.connect(**params)


def ensure_tables(conn) -> None:
    """Create the RAW tables if they do not exist yet."""
    statements = [s.strip() for s in DDL_PATH.read_text().split(";") if s.strip()]
    cur = conn.cursor()
    for stmt in statements:
        cur.execute(stmt)


def load_dataframe(conn, df: pd.DataFrame, table: str, database: str, schema: str = "RAW") -> int:
    if df.empty:
        log.warning("No rows to load into %s", table)
        return 0
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]  # Snowflake columns are uppercase
    snapshot_date = df["SNAPSHOT_DATE"].iloc[0]
    conn.cursor().execute(f"DELETE FROM {table} WHERE SNAPSHOT_DATE = %s", (snapshot_date,))
    _, _, nrows, _ = write_pandas(
        conn, df, table, database=database, schema=schema, use_logical_type=True
    )
    log.info("Loaded %s rows into %s.%s.%s", nrows, database, schema, table)
    return nrows
