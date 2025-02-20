import json
from datetime import datetime

import pandas as pd
from requests import Session

from constants import (
    COINMARKETCAP_API_KEY,
    EXHANGE_RATES_API_KEY,
    COINMARKETCAP_SYMBOLS,
    POSTGRES_TABLE_EXCHANGE_RATES,
    EXCHANGE_RATES_BASE,
    EXCHANGE_RATE_SYMBOLS,
)
from read_write_postgres import write_to_db, read_from_db


def make_request_cmc(session):
    response_api = session.get(
        url="https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
        headers={
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
        },
        params={
            "symbol": COINMARKETCAP_SYMBOLS,
            "convert": EXCHANGE_RATES_BASE,
        },
    )

    return response_api.json()


def make_request_exr(session):
    response_api = session.get(
        url="https://api.exchangeratesapi.io/v1/latest",
        params={
            "access_key": EXHANGE_RATES_API_KEY,
            "base": EXCHANGE_RATES_BASE,
            "symbols": EXCHANGE_RATE_SYMBOLS,
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
    latest_df = read_from_db(query)

    # convert 'date' column to datetime format
    df_temp_date = pd.DataFrame()
    df_temp_date["date"] = pd.to_datetime(latest_df["date"]).dt.date

    # get today's date
    today_date = datetime.today().date()

    if latest_df.empty or today_date > df_temp_date["date"].iloc[0]:
        # get todays exchange rate data from exchangerates API
        data_exr = make_request_exr(session)
        exchange_list = EXCHANGE_RATE_SYMBOLS.split(",")

        # remap the dictionary to store: date + timestamp + base + exchange rate
        remap = {"base": data_exr.get("base")} | {
            symbol: data_exr.get("rates").get(symbol) for symbol in exchange_list
        }

        # serialize for PostgreSQL compability
        data_json = {"date": data_exr.get("date"), "data": json.dumps(remap)}
        latest_df = pd.DataFrame.from_dict([data_json])

        # write exchange data into a dedicated table: "exchange_rates"
        write_to_db(latest_df, table_name)

        # ensures returned data is in correct serialized form as stored in the database
        latest_df = read_from_db(query)

    return latest_df.iloc[0].to_dict()


def get_data():
    s = Session()

    # get cryptocurrency data from CoinMarketCap API
    data_cmc = make_request_cmc(s)

    # check if exchange rates for today are already stored
    data_rates = exchange_data_check(s, POSTGRES_TABLE_EXCHANGE_RATES)
    data_cmc.pop("status")

    # remove tags field from data for each coin
    for key, value in data_cmc["data"].items():
        value[0].pop("tags")

    combined_data = {"coin_data": data_cmc["data"], "rates_data": data_rates}

    return combined_data


if __name__ == "__main__":
    print(get_data())
