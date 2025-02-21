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
st.set_page_config(page_title="Crypto Dashboard", layout="wide")

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

def get_volume_data(crypto,fiat):
    query_volume = f""" 
    ALTER TABLE crypto_data 
    ALTER COLUMN exchange_rates 
    SET DATA TYPE JSONB 
    USING exchange_rates::JSONB;
    SELECT DISTINCT ON (last_updated) last_updated, volume_24h, volume_change_24h, exchange_rates->>'{fiat}' AS {fiat}_rate
    FROM {POSTGRES_TABLE_COIN_DATA} 
    WHERE symbol ='{crypto}'
    ORDER BY last_updated; """

    df_volume = read_from_db(query_volume)
    
    if fiat in EXCHANGE_RATE_SYMBOLS.split(','):
        df_volume["volume_24h"] = df_volume["volume_24h"] * df_volume[f"{fiat.lower()}_rate"].astype(float)
         
    #print(df_volume)
    return df_volume

def get_general_data(crypto):
    query_volume = f""" 
    SELECT DISTINCT ON (last_updated) last_updated, cmc_rank, circulating_supply, total_supply
    FROM {POSTGRES_TABLE_COIN_DATA} 
    WHERE symbol ='{crypto}'
    ORDER BY last_updated DESC
    LIMIT 1; """

    df_volume = read_from_db(query_volume)
         
    print(df_volume)
    return df_volume

def format_large_numbers(num):
    if num >= 1e9:  # Billion
        return f"{num / 1e9:.1f}B"
    elif num >= 1e6:  # Million
        return f"{num / 1e6:.1f}M"
    elif num >= 1e3:  # Thousand
        return f"{num / 1e3:.1f}K"
    else:
        return str(int(num))
    
def layout():
       
    #Streamlit 
    
    st.title("📈 Live Cryptocurrency Dashboard")
    col1, col2 = st.columns(2)

    with col1:  
        selected_crypto = st.selectbox(label="Select crypto currency:",options=options_crypto)
    with col2:
        selected_currency = st.selectbox(label="Select fiat currency:",options=options_currency)
    
    # ------------------------   General info section  -------------------
    st.markdown(f"## {selected_crypto}: General information ")

    # Get general information about cryptocurrency
    df_gen = get_general_data(selected_crypto)
    print(type(df_gen["circulating_supply"].iloc[0]))

    gcol1, gcol2, gcol3 = st.columns(3)

    with gcol1:  
        st.metric("CMC rank", value=df_gen["cmc_rank"],border=True)
    with gcol2:
        st.metric("Circulating Supply (#coins)", value=format_large_numbers(df_gen["circulating_supply"].iloc[0]),border=True)
    with gcol3:
        st.metric("Total Supply (#coins)", value=format_large_numbers(df_gen["total_supply"].iloc[0]),border=True)

    # ------------------------   Header for price section  -------------------
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
    
    # ------------------- Header for volume section   -------------------
    st.markdown(f"## {selected_crypto}: Volume trends in {selected_currency} ")

    # Get  volume data
    df_volume = get_volume_data(selected_crypto, selected_currency)
    
    # Select type of volume trend
    options_volume= ["Volume 24h", "Volume Change 24h"]
    selection_volume = st.segmented_control(
    "Type of trend", options_volume, selection_mode="single", default=options_volume[0]
    )

    volume_field = selection_volume.lower().replace(" ","_")
    print(f"{volume_field=}")
    # Volume trend Chart
    labels_volume = {
        "last_updated" : "Timestamp",
        "volume_24h" : selected_currency,
        "volume_change_24h" : "%",
       }

    fig_volume = px.line(df_volume, x='last_updated', y=volume_field, labels=labels_volume)
    
   
    st.plotly_chart(fig_volume, use_container_width=True)

    # ------------------- Header for market cap section   -------------------
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

