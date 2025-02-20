import streamlit as st
import pandas as pd
import json
import plotly.express as px
from constants import (
    POSTGRES_TABLE_COIN_DATA,
    EXCHANGE_RATES_BASE,
    EXCHANGE_RATE_SYMBOLS,
)
from read_write_postgres import read_from_db


query_p = f"""
ALTER TABLE crypto_data ALTER COLUMN exchange_rates SET DATA TYPE JSONB USING exchange_rates::JSONB;
SELECT DISTINCT ON (symbol, last_updated)
    symbol,
    last_updated,
    price,
    exchange_rates
FROM {POSTGRES_TABLE_COIN_DATA}
ORDER BY last_updated, symbol, price    ;
"""

df_crypto = read_from_db(query_p)


options_crypto = ["XRP", "TRX"]
selection_crypto = st.selectbox(
    label="Select Crypto",
    options=options_crypto,
)

df_crypto = df_crypto[df_crypto["symbol"] == selection_crypto]


options_currency = [EXCHANGE_RATES_BASE] + EXCHANGE_RATE_SYMBOLS.split(",")
selection_currency = st.selectbox(
    label="Select Crypto",
    options=options_currency,
)

df_return = pd.DataFrame()
df_return["price"] = df_crypto["price"] * df_crypto["exchange_rates"].apply(
    lambda x: x.get(selection_currency, 1)
)
df_return["last_updated"] = df_crypto["last_updated"]


st.header(selection_crypto)
st.table(df_return)

fig = px.line(df_return, x="last_updated", y="price")
st.plotly_chart(fig, use_container_width=True)
