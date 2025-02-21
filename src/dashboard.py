import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from read_write_postgres import read_from_db
from constants import (
    POSTGRES_TABLE_COIN_DATA,
    COINMARKETCAP_SYMBOLS,
    EXCHANGE_RATES_BASE,
    EXCHANGE_RATE_SYMBOLS,
    )
options_currency = [EXCHANGE_RATES_BASE] + EXCHANGE_RATE_SYMBOLS.split(',') 
options_crypto = COINMARKETCAP_SYMBOLS.split(',')

# Auto-refresh every 20 seconds
count = st_autorefresh(interval=20 * 1000, limit=100, key="data_refresh")

def get_price_data(crypto, fiat):
    query_price = f""" 
    ALTER TABLE crypto_data 
    ALTER COLUMN exchange_rates 
    SET DATA TYPE JSONB 
    USING exchange_rates::JSONB;
    SELECT DISTINCT ON (last_updated) last_updated, price, exchange_rates->>'{fiat}' AS {fiat}_rate 
    FROM {POSTGRES_TABLE_COIN_DATA} 
    WHERE symbol ='{crypto}'
    ORDER BY last_updated, price ; """

    df_crypto = read_from_db(query_price)
    print(df_crypto)

    if fiat in EXCHANGE_RATE_SYMBOLS.split(','):
        df_crypto["price"] = df_crypto["price"] * df_crypto[f"{fiat.lower()}_rate"].astype(float)
    
    
    return df_crypto

def get_market_cap_data(crypto,fiat):
    query_mcap = f""" 
    ALTER TABLE crypto_data 
    ALTER COLUMN exchange_rates 
    SET DATA TYPE JSONB 
    USING exchange_rates::JSONB;
    SELECT DISTINCT ON (last_updated) last_updated, market_cap,  market_cap_dominance, fully_diluted_market_cap, 
                                                    exchange_rates->>'{fiat}' AS {fiat}_rate 
    FROM {POSTGRES_TABLE_COIN_DATA} 
    WHERE symbol ='{crypto}'
    ORDER BY last_updated; """

    df_mcap = read_from_db(query_mcap)
    
    if fiat in EXCHANGE_RATE_SYMBOLS.split(','):
        df_mcap["market_cap"] = df_mcap["market_cap"] * df_mcap[f"{fiat.lower()}_rate"].astype(float)
        df_mcap["fully_diluted_market_cap"] = df_mcap["fully_diluted_market_cap"] * df_mcap[f"{fiat.lower()}_rate"].astype(float)   
    # print(df_mcap)
    return df_mcap


def layout():
       
    #Streamlit 
    #st.set_page_config(page_title="Crypto Dashboard", layout="wide")
    st.title("📈 Live Cryptocurrency Dashboard")
    col1, col2 = st.columns(2)

    with col1:  
        selected_crypto = st.selectbox(label="Select crypto currency:",options=options_crypto)
    with col2:
        selected_currency = st.selectbox(label="Select fiat currency:",options=options_currency)
    
    # Header for price section  
    st.markdown(f"## {selected_crypto}: Latest price in {selected_currency} ")
    
    # Get price data
    df_crypto = get_price_data(selected_crypto, selected_currency)

    # Price Chart
    labels_price = {
        "last_updated" : "Timestamp",
        "price" : selected_currency,
    }

    fig_price = px.line(df_crypto, x='last_updated', y='price', labels=labels_price)
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Header for market cap section   
    st.markdown(f"## {selected_crypto}: Market cap trends in {selected_currency} ")

    # Get marketcap data
    df_mcap = get_market_cap_data(selected_crypto, selected_currency)
    
    # Select type of marketcap trend
    options_mcap= ["Market Cap", "Market Cap Dominance", "Fully Diluted Market Cap"]
    selection_mcap = st.segmented_control(
    "Type of trend", options_mcap, selection_mode="single", default=options_mcap[0]
    )

    mcap_field = selection_mcap.lower().replace(" ","_")
    # Market Cap trend Chart
    labels_mcap = {
        "last_updated" : "Timestamp",
        "market_cap" : selected_currency,
        "market_cap_dominance" : "%",
        "fully_diluted_market_cap" : selected_currency,
    }

    fig_mcap = px.line(df_mcap, x='last_updated', y=mcap_field, labels=labels_mcap)
   
    st.plotly_chart(fig_mcap, use_container_width=True)


    

if __name__ == "__main__":
    layout()

