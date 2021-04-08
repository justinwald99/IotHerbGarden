"""Manager for the garden.

This module handles logging sensor values to the database as
well as the automation of watering events.

"""
from datetime import datetime
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, Integer, MetaData,
                        String, Table, create_engine, insert)
import pandas as pd

engine = create_engine("sqlite+pysqlite:///garden.db", echo=True, future=True)
metadata = MetaData()


def create_db():
    """Create an instance of the DB if one does not already exist."""
    Table(
        "sensor",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("unit", String),
        Column("sample_rate_hz", Integer, )
    )

    Table(
        "sample",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("sensor_id", ForeignKey("sensor.id"), nullable=False),
        Column("timestamp", TIMESTAMP),
        Column("value", Integer)
    )

    metadata.create_all(engine)


def create_sensor(id, name, unit, sample_rate_hz):
    """Create a sensor in the database."""
    with engine.connect() as conn:
        conn.execute(insert(metadata.tables["sensor"]),
                     [{
                         "id": "id",
                         "name": "name",
                         "unit": "unit",
                         "sample_rate_hz": "sample_rate_hz"
                     }]
                     )
        conn.commit()


def create_sample(id, sensor_id, timestamp, value):
    """Create a sensor entry in the database."""
    with engine.connect() as conn:
        conn.execute(insert(metadata.tables["sample"]),
                     [{
                         "id": id,
                         "sensor_id": sensor_id,
                         "timestamp": datetime.now(),
                         "value": value
                     }]
                     )
        conn.commit()


if (__name__ == "__main__"):
    create_db()
    df = pd.read_csv("data/example_data.csv")
