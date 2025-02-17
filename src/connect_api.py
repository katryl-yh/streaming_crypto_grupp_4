from constants import COINMARKETCAP_API_KEY, EXHANGE_RATES_API_KEY, SYMBOLS
from requests import Session
from pprint import pprint
from read_write_postgres import write_to_db, read_from_db
import pandas as pd
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
            "id": SYMBOLS,
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


def get_data():
    # get cryptocurrency data from CoinMarketCap API
    s = Session()
    #data_cmc = make_request_cmc(s)
    # get exchange rate data from exchangerates API
    data_exr = make_request_exr(s)
    exchange_list = EXCHANGE_SYMBOLS.split(',')
    # remap the dictionary to store: date + timestamp + base + exchange rate 
    remap = {"date": data_exr.get("date"), 
             "timestamp": data_exr.get("timestamp"),
             "base": data_exr.get("base"),
             }

    remap = remap | {symbol: data_exr.get("rates").get(symbol) for symbol in exchange_list}
 
    df = pd.DataFrame.from_dict([remap])
    print("This is data that we send to database:")
    print(df.head())

    # write exchange data into a dedicated table: "exchange_rates"
    write_to_db(df,table_nm)

    # test read data from a dedicated table: "exchange_rates"
    query = """SELECT * 
            FROM exchange_rates; """
            #ORDER BY date DESC
            #LIMIT 1;"""
    return read_from_db(table_nm,query)


if __name__ == "__main__":
    print("This is the data that we get from database:")
    pprint(get_data())

