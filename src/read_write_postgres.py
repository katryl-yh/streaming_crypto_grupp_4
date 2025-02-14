from sqlalchemy import create_engine
from constants import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)

import pandas as pd

data = {'name': ['nick', 'david', 'joe', 'ross'],'age': ['5', '10', '7', '6']}
data = pd.DataFrame.from_dict(data)
print(data.head())

postgres_connection = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

data.to_sql(
    "exchange_rates", postgres_connection, schema="public", if_exists="replace", index=False
            )
