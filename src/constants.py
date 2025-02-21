import dotenv
import os

dotenv.load_dotenv()

# Loading enviorment variables with a default values in case of not present in .env file
# os.getenv(<VARIABLE NAME>, <default value if not exists>)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")
EXHANGE_RATES_API_KEY = os.getenv("EXHANGE_RATES_API_KEY", "")

KAFKA_HOST = os.getenv("KAFKA_HOST", "localhost")
KAFKA_PORT = os.getenv("KAFKA_PORT", 9092)
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "coin_group")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "coin_topic")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")

POSTGRES_DB = os.getenv("POSTGRES_DB", "coin_data")
POSTGRES_TABLE_EXCHANGE_RATES = os.getenv(
    "POSTGRES_TABLE_EXCHANGE_RATES", "exchange_rates"
)
POSTGRES_TABLE_COIN_DATA = os.getenv("POSTGRES_TABLE_COIN_DATA", "crypto_data")

COINMARKETCAP_SYMBOLS = os.getenv("COINMARKETCAP_SYMBOLS", "XRP,TRX")
EXCHANGE_RATES_BASE = "EUR" # os.getenv("EXCHANGE_RATES_BASE", "EUR") free account limitation
EXCHANGE_RATE_SYMBOLS = os.getenv("EXCHANGE_RATE_SYMBOLS", "DKK,NOK,SEK")

UPDATE_FREQ_SEC = int(os.getenv("UPDATE_FREQ_SEC", 60))

if __name__ == "__main__":
    if not (COINMARKETCAP_API_KEY and EXHANGE_RATES_API_KEY):
        raise ValueError("API keys not found.")
