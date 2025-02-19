import json

from constants import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    POSTGRES_TABLE_COIN_DATA,
    KAFKA_HOST,
    KAFKA_PORT,
    KAFKA_CONSUMER_GROUP,
    KAFKA_TOPIC,
)
from quixstreams import Application
from quixstreams.sinks.community.postgresql import PostgreSQLSink


def create_postgres_sink():
    return PostgreSQLSink(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        table_name=POSTGRES_TABLE_COIN_DATA,
        schema_auto_update=True,
    )


def transform_data(data):
    # next(iter(<iterable>)) gives first value of iterable
    coin_data = next(iter(data.get("coin_data").values()))
    crypto_data = next(iter(coin_data))
    base_currency = next(iter(crypto_data.get("quote").keys()))
    quote_data = crypto_data.get("quote").get(base_currency)

    exchange_rates_data = data.get("rates_data").get("data")
    exchange_rates_base = exchange_rates_data.pop("base")

    base_record = {
        "symbol": crypto_data.get("symbol"),
        "last_updated": quote_data.get("last_updated"),
        "base_currency": base_currency,
        "price": quote_data.get("price"),
        "circulating_supply": crypto_data.get("circulating_supply"),
        "total_supply": crypto_data.get("total_supply"),
        "market_cap": quote_data.get("market_cap"),
        "market_cap_dominance": quote_data.get("market_cap_dominance"),
        "fully_diluted_market_cap": quote_data.get("fully_diluted_market_cap"),
        "percent_change_1h": quote_data.get("percent_change_1h"),
        "percent_change_24h": quote_data.get("percent_change_24h"),
        "percent_change_7d": quote_data.get("percent_change_7d"),
        "percent_change_30d": quote_data.get("percent_change_30d"),
        "percent_change_60d": quote_data.get("percent_change_60d"),
        "percent_change_90d": quote_data.get("percent_change_90d"),
        "volume_24h": quote_data.get("volume_24h"),
        "volume_change_24h": quote_data.get("volume_change_24h"),
        "cmc_rank": crypto_data.get("cmc_rank"),
    }

    if base_currency == exchange_rates_base:
        # Serialize JSON for PostgreSQL compability
        base_record["exchange_rates"] = json.dumps(exchange_rates_data)

    return base_record


def main():
    app = Application(
        broker_address=f"{KAFKA_HOST}:{KAFKA_PORT}",
        consumer_group=KAFKA_CONSUMER_GROUP,
        auto_offset_reset="earliest",
    )

    topic_coins = app.topic(
        name=KAFKA_TOPIC,
        value_deserializer="json",
    )

    sdf = app.dataframe(topic=topic_coins)

    sdf = sdf.apply(transform_data)

    sdf.update(
        lambda x: print(f"Transformed data: {x.get('symbol')} {x.get('last_updated')}")
    )

    sdf.sink(create_postgres_sink())

    app.run()


if __name__ == "__main__":
    main()
