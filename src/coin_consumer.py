from quixstreams import Application
# from quixstreams.sinks.community.postgresql import PostgreSQLSink
from constants import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    KAFKA_HOST,
    KAFKA_PORT,
)
CONSUMER_GROUP = "coin_group"
TOPIC_NAME = "coins"

def main():

    app = Application(
        broker_address=f"{KAFKA_HOST}:{KAFKA_PORT}",
        consumer_group=CONSUMER_GROUP,
        auto_offset_reset="earliest",
    )

    coins_topic = app.topic(name=TOPIC_NAME, value_deserializer="json")

    sdf = app.dataframe(topic=coins_topic)

    sdf.update(lambda coin_data: print(coin_data))

    app.run()


if __name__ == "__main__":
    main()