from constants import COINMARKETCAP_API_KEY, EXHANGE_RATES_API_KEY, SYMBOLS
from requests import Session
from pprint import pprint


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
    s = Session()
    data_cmc = make_request_cmc(s)
    data_exr = make_request_exr(s)


if __name__ == "__main__":
    get_data()
