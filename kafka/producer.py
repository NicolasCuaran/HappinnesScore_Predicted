# producer.py

import os
import json
import time
import logging
from dotenv import load_dotenv

import pandas as pd
import country_converter as coco
from sklearn.model_selection import train_test_split
from kafka import KafkaProducer

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")

load_dotenv("./env")

# Funciones de extracción y transformación

def extracting_data():
    logging.info("Extracting data from CSV files.")
    years = ["2015", "2016", "2017", "2018", "2019"]
    dfs = {year: pd.read_csv(f"./data/{year}.csv") for year in years}
    logging.info("Data extracted successfully.")
    return dfs

# Normalización de nombres de columnas

def normalize_columns(happiness_dataframes: dict) -> dict:    
    column_mapping = {    
        "Country": "country",
        "Country or region": "country",
        "Happiness Score": "happiness_score",
        "Happiness.Score": "happiness_score",
        "Score": "happiness_score",
        "Happiness Rank": "happiness_rank",
        "Happiness.Rank": "happiness_rank",
        "Overall rank": "happiness_rank",
        "Economy (GDP per Capita)": "economy",
        "Economy..GDP.per.Capita.": "economy",
        "GDP per capita": "economy",
        "Health (Life Expectancy)": "health",
        "Health..Life.Expectancy.": "health",
        "Healthy life expectancy": "health",
        "Family": "social_support",
        "Social support": "social_support",
        "Freedom": "freedom",
        "Freedom to make life choices": "freedom",
        "Trust (Government Corruption)": "corruption_perception",
        "Trust..Government.Corruption.": "corruption_perception",
        "Perceptions of corruption": "corruption_perception",
        "Generosity": "generosity",
        "Dystopia Residual": "dystopia_residual",
        "Dystopia.Residual": "dystopia_residual",
    }
    for year, df in happiness_dataframes.items():
        happiness_dataframes[year] = df.rename(columns=column_mapping)
    return happiness_dataframes

# Agregar año y concatenar

def add_year_column(hdfs: dict) -> dict:
    for year, df in hdfs.items():
        df['year'] = year
    return hdfs


def concatenate_common_columns(hdfs: dict) -> pd.DataFrame:
    common = set(hdfs[next(iter(hdfs))].columns)
    for df in hdfs.values():
        common &= set(df.columns)
    return pd.concat([df[list(common)] for df in hdfs.values()], ignore_index=True)

# Rellenar NA

def fill_na_with_mean(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df[col] = df[col].fillna(df[col].mean())
    return df

# Agregar continente

def add_continent_column(df: pd.DataFrame) -> pd.DataFrame:
    cc = coco.CountryConverter()
    df['continent'] = cc.convert(names=df['country'].tolist(), to='continent')
    continent_mapping = {
        "Canada": "North America",
        "Costa Rica": "Central America",
        "Mexico": "North America",
        "United States": "North America",
        "Brazil": "South America",
        "Venezuela": "South America",
        "Panama": "Central America",
        "Chile": "South America",
        "Argentina": "South America",
        "Uruguay": "South America",
        "Colombia": "South America",
        "Suriname": "South America",
        "Trinidad and Tobago": "South America",
        "El Salvador": "Central America",
        "Guatemala": "Central America",
        "Ecuador": "South America",
        "Bolivia": "South America",
        "Paraguay": "South America",
        "Nicaragua": "Central America",
        "Peru": "South America",
        "Jamaica": "Central America",
        "Dominican Republic": "Central America",
        "Honduras": "Central America",
        "Haiti": "Central America",
        "Puerto Rico": "Central America",
        "Belize": "Central America",
        "Trinidad & Tobago": "South America"
    }
    df['continent'] = df['country'].map(continent_mapping).fillna(df['continent'])
    return df

# Transformación completa

def transforming_data(hdfs: dict) -> pd.DataFrame:
    logging.info("Starting transformation process.")
    hdfs = normalize_columns(hdfs)
    hdfs = add_year_column(hdfs)
    df = concatenate_common_columns(hdfs)
    df = fill_na_with_mean(df, 'corruption_perception')
    df = add_continent_column(df)
    order = [
        'country', 'continent', 'year', 'economy', 'health', 'social_support',
        'freedom', 'corruption_perception', 'generosity', 'happiness_rank', 'happiness_score'
    ]
    df = df[order]
    logging.info("Transformation completed.")
    return df

# Preprocesamiento: dummies y split

def creating_dummy_variables(df: pd.DataFrame) -> pd.DataFrame:
    df = pd.get_dummies(df, columns=['continent'])
    return df.rename(columns={
        'continent_North America':'continent_North_America',
        'continent_Central America':'continent_Central_America',
        'continent_South America':'continent_South_America'
    })


def splitting_data(df: pd.DataFrame):
    X = df.drop(['happiness_score','happiness_rank','country'], axis=1)
    y = df['happiness_score']
    return train_test_split(X, y, test_size=0.3, random_state=200)


def preprocessing_data(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Starting preprocessing.")
    df = creating_dummy_variables(df)
    X_train, X_test, y_train, y_test = splitting_data(df)
    X_test['id'] = X_test.index
    X_test['happiness_score'] = y_test.values
    order = [
        'id', 'year', 'economy', 'health', 'social_support', 'freedom',
        'corruption_perception', 'generosity', 'happiness_score',
        'continent_Africa', 'continent_Asia', 'continent_Central_America',
        'continent_Europe', 'continent_North_America', 'continent_Oceania',
        'continent_South_America'
    ]
    X_test = X_test[order]
    logging.info("Preprocessing completed.")
    return X_test

# Función para enviar a Kafka

def get_kafka_producer(df: pd.DataFrame, topic: str) -> None:
    logging.info(f'Starting to send messages to topic "{topic}".')
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for _, row in df.iterrows():
        producer.send(topic, value=row.to_dict())
        time.sleep(1)
        logging.info('Message sent to Kafka.')
    producer.close()

# Bloque principal

if __name__ == '__main__':
    logging.info("Starting Producer script.")
    hdfs = extracting_data()
    df = transforming_data(hdfs)
    df = preprocessing_data(df)
    get_kafka_producer(df, 'whr_kafka_topic')
    logging.info("Producer script completed.")
