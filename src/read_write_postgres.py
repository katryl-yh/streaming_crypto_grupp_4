from sqlalchemy import create_engine
from constants import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)

import pandas as pd

postgres_connection = create_engine(
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

# write function to postgres, TO DO: add error handling later to know if we succeded
def write_to_db(dataframe,table_name):   
    dataframe.to_sql(
    table_name, 
    postgres_connection, 
    schema="public", 
    if_exists="replace", 
    index=False
    )

# read function from postgres, TO DO: add error handling later to know if we succeded
def read_from_db(table_name, sql_query):   
    return pd.read_sql(
        sql_query,
        postgres_connection,
    )
