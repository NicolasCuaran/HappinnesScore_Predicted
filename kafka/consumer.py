# consumer.py

import os
import sys
import json
import time
import logging
from dotenv import load_dotenv

import pandas as pd
from kafka import KafkaProducer, KafkaConsumer
import joblib
from sqlalchemy import (
    create_engine, inspect, MetaData, Table, Column,
    Integer, Float, String, Text, DateTime, Boolean
)
from sqlalchemy_utils import database_exists, create_database
import country_converter as coco

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p"
)

load_dotenv("./env")
user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
host = os.getenv("PG_HOST")
port = os.getenv("PG_PORT")
database = os.getenv("PG_DATABASE")

def get_kafka_consumer(topic: str) -> list:
    logging.info(f'Starting to listen to topic "{topic}".')
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers="localhost:9092",
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            consumer_timeout_ms=3000,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        data = []
        for kafka_message in consumer:
            message = kafka_message.value
            data.append(message)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            offset = kafka_message.offset
            logging.info(f"Message with offset {offset} received at {timestamp}: {message}")
        consumer.close()
        logging.info("Consumer closed.")
        return data
    except Exception as e:
        logging.exception(f"An error was encountered: {e}")
        return []

def get_kafka_producer(df: pd.DataFrame, topic: str) -> None:
    logging.info(f'Starting to send messages to topic "{topic}".')
    try:
        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        for _, row in df.iterrows():
            producer.send(topic, value=dict(row))
            time.sleep(1)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            logging.info(f"Message sent at {timestamp}")
        producer.close()
    except Exception as e:
        logging.exception(f"An error was encountered: {e}")

def creating_engine():
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)
    if not database_exists(url):
        create_database(url)
        logging.info(f'The database "{database}" was created.')
    logging.info("Engine created.")
    return engine

def disposing_engine(engine):
    engine.dispose()
    logging.info("Engine disposed.")

def infering_types(dtype, column_name, df):
    if "int" in dtype.name:
        return Integer
    elif "float" in dtype.name:
        return Float
    elif "object" in dtype.name:
        max_len = df[column_name].astype(str).str.len().max()
        return Text if max_len > 255 else String(255)
    elif "datetime" in dtype.name:
        return DateTime
    elif "bool" in dtype.name:
        return Boolean
    else:
        return Text

def load_clean_data(engine, df: pd.DataFrame, table_name: str) -> None:
    logging.info(f"Creating table {table_name}.")
    try:
        if not inspect(engine).has_table(table_name):
            metadata = MetaData()
            columns = [
                Column(name, infering_types(dtype, name, df), primary_key=(name=="id"))
                for name, dtype in df.dtypes.items()
            ]
            table = Table(table_name, metadata, *columns)
            table.create(engine)
            df.to_sql(table_name, con=engine, if_exists="append", index=False)
            logging.info(f"Table {table_name} created and data loaded.")
        else:
            logging.error(f"Table {table_name} already exists.")
    except Exception as e:
        logging.exception(f"Error creating table {table_name}: {e}")

if __name__ == "__main__":
    logging.info("Starting the Consumer script.")

    # 1) Consumir mensajes
    consumer_messages = get_kafka_consumer("whr_kafka_topic")
    if not consumer_messages:
        logging.error("No messages consumed, saliendo.")
        sys.exit(1)

    # 2) Convertir a DataFrame
    df = pd.DataFrame(consumer_messages)

    # 3) Cargar modelo y preparar X
    rf_model = joblib.load("./model/rf_model.pkl")
    try:
        feature_cols = list(rf_model.feature_names_in_)
    except AttributeError:
        feature_cols = [c for c in df.columns if c not in ("id", "happiness_score")]

    missing = set(feature_cols) - set(df.columns)
    for col in missing:
        df[col] = 0
    df_test = df[feature_cols]

    # 4) Predecir
    predictions = rf_model.predict(df_test)
    df["predicted_happiness_score"] = predictions

    # 5) Reordenar columnas
    new_order = [
        'id','year','economy','health','social_support','freedom',
        'corruption_perception','generosity','continent_Africa','continent_Asia',
        'continent_Europe','continent_North_America','continent_Central_America',
        'continent_South_America','continent_Oceania','happiness_score',
        'predicted_happiness_score'
    ]
    df = df.reindex(columns=new_order, fill_value=None)

    # 6) Cargar en BD
    engine = creating_engine()
    load_clean_data(engine, df, "whr_predictions")
    disposing_engine(engine)

    logging.info("Consumer script completed.")
