# db_loader.py
import pandas as pd
from sqlalchemy import create_engine


def load_table(table_name):
    """
    Load an entire table from the PostgreSQL database into a Pandas DataFrame.

    Parameters
    ----------
    table_name : str
        Name of the table to load (case-sensitive, use quotes if needed)

    Returns
    -------
    DataFrame
        A pandas DataFrame containing the table's data.
    """
    # Database connection string
    DB_CONNECTION_STRING = 'postgresql+psycopg2://postgres:GRMWCMSE$@34.46.50.129:5432/'+table_name

    # Create engine only once
    engine = create_engine(DB_CONNECTION_STRING)

    sql = f'SELECT * FROM "{table_name}";'  # Quotes handle case sensitivity
    return pd.read_sql(sql, con=engine, index_col = 'Unnamed: 0')
