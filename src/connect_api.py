from constants import COINMARKETCAP_API_KEY, EXHANGE_RATES_API_KEY, SYMBOLS
from requests import Session
from pprint import pprint
from read_write_postgres import write_to_db, read_from_db
import pandas as pd
from datetime import datetime
import json

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


def exchange_data_check(session, table_name):
    # read data from a table dedicated to exchange rates to get the latest data
    query = f"""SELECT * 
            FROM {table_name}
            ORDER BY date DESC
            LIMIT 1;"""

    # read_from_db returns data in form of a dataframe
    latest_df = read_from_db(table_name, query)

    # Convert 'date' column to datetime format
    latest_df["date"] = pd.to_datetime(latest_df["date"]).dt.date

    # Get today's date
    today_date = datetime.today().date()

    if latest_df.empty or today_date > latest_df["date"].iloc[0]:
        # get todays exchange rate data from exchangerates API
        data_exr = make_request_exr(session)
        exchange_list = EXCHANGE_SYMBOLS.split(",")

        # remap the dictionary to store: date + timestamp + base + exchange rate
        remap = {"base": data_exr.get("base")} | {
            symbol: data_exr.get("rates").get(symbol) for symbol in exchange_list
        }
        data_json = {"date": data_exr.get("date"), "data": json.dumps(remap)}
        latest_df = pd.DataFrame.from_dict([data_json])

        # write exchange data into a dedicated table: "exchange_rates"
        write_to_db(latest_df, table_nm)

    return latest_df.iloc[0].to_dict()


def get_data():
    s = Session()

    # get cryptocurrency data from CoinMarketCap API
    data_cmc = make_request_cmc(s)

    # check if exchange rates for today are already stored
    rates_check = exchange_data_check(s, table_nm)

    return data_cmc, rates_check


if __name__ == "__main__":
    pprint(get_data())
