from constants import COINMARKETCAP_API_KEY, EXHANGE_RATES_API_KEY, SYMBOLS
from requests import Session
from pprint import pprint
from read_write_postgres import write_to_db, read_from_db
import pandas as pd


def make_request_cmc(session):
    response_api = session.get(
        url="https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
        headers={
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
        },
        params={
            "id": SYMBOLS,
            "convert": "EUR",
        },
    )

    return response_api.json()


def make_request_exr(session):
    response_api = session.get(
        url="https://api.exchangeratesapi.io/v1/latest",
        params={
            "access_key": EXHANGE_RATES_API_KEY,
            "base": "EUR",
            "symbols": "DKK,NOK,SEK",
        },
    )

    return response_api.json()


def get_data():
    # 1. call function exchange data from exchange API
    s = Session()
    #data_cmc = make_request_cmc(s)
    data_exr = make_request_exr(s)
    # TO DO: reshape the dictionary, so that we have 1 row with columns for each exchange rate + timestamp + data + base 
    df = pd.DataFrame.from_dict(data_exr)
    # 2. test write function with exchange data
    table_nm = "exchange_rates"
    write_to_db(df,table_nm)

    # 3. test read function with exchange data
    query = """SELECT * FROM exchange_rates;"""
    return read_from_db(table_nm,query)


if __name__ == "__main__":
    pprint(get_data())

