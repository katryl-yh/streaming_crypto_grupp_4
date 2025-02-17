from constants import COINMARKETCAP_API_KEY, EXHANGE_RATES_API_KEY, SYMBOLS
from requests import Session
from pprint import pprint
from read_write_postgres import write_to_db, read_from_db
import pandas as pd
from datetime import datetime
table_nm = "exchange_rates"
EXCHANGE_BASE = "EUR"
EXCHANGE_SYMBOLS = "DKK,NOK,SEK"


def make_request_cmc(session):
    response_api = session.get(
        url="https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
        headers={
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
        },
        params={
            "symbol": SYMBOLS,
            "convert": EXCHANGE_BASE,
        },
    )

    return response_api.json()


def make_request_exr(session):
    response_api = session.get(
        url="https://api.exchangeratesapi.io/v1/latest",
        params={
            "access_key": EXHANGE_RATES_API_KEY,
            "base": EXCHANGE_BASE,
            "symbols": EXCHANGE_SYMBOLS,
        },
    )

    return response_api.json()

def exchange_data_check(table_name):
    # Get today's date
    today_date = datetime.today().date()

    # read data from a table dedicated to exchange rates to get the latest data
    query = f"""SELECT * 
            FROM {table_name}
            ORDER BY date DESC
            LIMIT 1;"""
    
    latest_data = read_from_db(table_name,query)

    # save the data into a dataframe
    latest_df = pd.DataFrame(latest_data)

    # Convert 'date' column to datetime format
    latest_df["date"] = pd.to_datetime(latest_df["date"]).dt.date 

    # Compare dates
    if latest_df["date"].iloc[0] == today_date:
        #print("The dates match!")
        return True
    else:
        #print(f"The dates do not match. DB date: {latest_df['date'].iloc[0]}, Today's date: {today_date}")
        return False 


def get_data():
    # get cryptocurrency data from CoinMarketCap API
    s = Session()
    data_cmc = make_request_cmc(s)

    # check if exchange rates for today are already stored
    rates_check = exchange_data_check(table_nm)
    if rates_check != True:
        # get todays exchange rate data from exchangerates API
        data_exr = make_request_exr(s)
        exchange_list = EXCHANGE_SYMBOLS.split(',')
        # remap the dictionary to store: date + timestamp + base + exchange rate 
        remap = {"date": data_exr.get("date"), 
                "timestamp": data_exr.get("timestamp"),
                "base": data_exr.get("base"),
                }

        remap = remap | {symbol: data_exr.get("rates").get(symbol) for symbol in exchange_list}
    
        df = pd.DataFrame.from_dict([remap])
        #print("This is data that we send to database:")
        #print(df.head())

        # write exchange data into a dedicated table: "exchange_rates"
        write_to_db(df,table_nm)

    # read data from a table dedicated to exchange rates to get the latest data
    query = f"""SELECT * 
            FROM {table_nm}
            ORDER BY date DESC
            LIMIT 1;"""
    
    data_exchange = read_from_db(table_nm,query)
    
    return data_cmc, data_exchange


if __name__ == "__main__":
    pprint(get_data())

    

