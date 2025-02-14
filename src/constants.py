import dotenv
import os

dotenv.load_dotenv()

# Loading enviorment variables with a default values in case of not present in .env file
# os.getenv(<VARIABLE NAME>, <default value if not exists>)

KAFKA_HOST = os.getenv("KAFKA_HOST", "localhost")
KAFKA_PORT = os.getenv("KAFKA_PORT", 9092)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")

COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")
EXHANGE_RATES_API_KEY = os.getenv("EXHANGE_RATES_API_KEY", "")

SYMBOLS = os.getenv("SYMBOLS", "XRP,TRON")

if __name__ == "__main__":
    if not(COINMARKETCAP_API_KEY and EXHANGE_RATES_API_KEY):
        raise ValueError("API keys not found.")