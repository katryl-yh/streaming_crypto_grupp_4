import json
import time

from connect_api import get_data
from constants import (
    KAFKA_HOST,
    KAFKA_PORT,
    KAFKA_CONSUMER_GROUP,
    KAFKA_TOPIC,
)
from quixstreams import Application

UPDATE_FREQ_SEC = 10


app = Application(
    broker_address=f"{KAFKA_HOST}:{KAFKA_PORT}",
    consumer_group=KAFKA_CONSUMER_GROUP,
)

topic_coins = app.topic(
    name=KAFKA_TOPIC,
    value_serializer="json",
)


def main():
    with app.get_producer() as producer:
        while True:
            data = get_data()
            rates_data = data.get("rates_data", {})

            for crypto_symbol, crypto_data in data.get("coin_data").items():
                data_remap = {
                    "coin_data": {crypto_symbol: crypto_data},
                    "rates_data": rates_data,
                }

                kafka_message = topic_coins.serialize(
                    key=crypto_symbol,
                    value=data_remap,
                )

                print(
                    f"Produce event with key: {kafka_message.key} ({kafka_message.value[:50]} ...)"
                )

                producer.produce(
                    topic=topic_coins.name,
                    key=kafka_message.key,
                    value=kafka_message.value,
                )

            time.sleep(UPDATE_FREQ_SEC)


if __name__ == "__main__":
    main()
