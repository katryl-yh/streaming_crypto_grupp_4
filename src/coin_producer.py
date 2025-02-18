from quixstreams import Application
from connect_api import get_data
from pprint import pprint
import time

app = Application(
    broker_address="localhost:9092",
    consumer_group="coin_group",
)

coins_topic = app.topic(name="coins", value_serializer="json")

def main():

    with app.get_producer() as producer:
        while True:
            coin_latest = get_data()

            kafka_message = coins_topic.serialize(
                key="coin_key", value=coin_latest
            )

            print(
                f"produce event with key = {kafka_message.key}, value = {coin_latest['coin_data'].keys()}"
            )
            producer.produce(
                topic=coins_topic.name, key=kafka_message.key, value=kafka_message.value
            )

            time.sleep(5)


if __name__ == "__main__":
    main()
    #pprint(get_latest_coin_data("BTC")["quote"])