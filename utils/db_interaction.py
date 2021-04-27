"""Utility functions for interacting with the database."""

from sqlalchemy import (TIMESTAMP, Column, ForeignKey, Integer, MetaData,
                        String, Table, create_engine)
from sqlalchemy.dialects.sqlite import insert

# Engine used to interface the db
engine = create_engine("sqlite+pysqlite:///garden.db", future=True)

# Metadata that keeps track of db schema
metadata = MetaData()

# Schema object for sensors
sensor_table = Table(
    "sensor",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String, nullable=False),
    Column("name", String, nullable=False),
    Column("unit", String, nullable=False),
    Column("sample_gap", Integer, nullable=False)
)

# Schema object for samples
sample_table = Table(
    "sample",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sensor_id", ForeignKey("sensor.id"), nullable=False),
    Column("timestamp", TIMESTAMP, nullable=False),
    Column("value", Integer, nullable=False)
)

# Schema object for plants
plant_table = Table(
    "plant",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("humidity_sensor_id", ForeignKey("sensor.id"), nullable=False),
    Column("pump_id", Integer, nullable=False),
    Column("target", Integer, nullable=False),
    Column("watering_cooldown", Integer, nullable=False),
    Column("watering_duration", Integer, nullable=False),
    Column("humidity_tolerance", Integer, nullable=False)
)

# Schema object for watering events
watering_table = Table(
    "watering_event",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("plant_id", ForeignKey("plant.id"), nullable=False),
    Column("timestamp", TIMESTAMP, nullable=False),
    Column("duration", Integer, nullable=False)
)


def initialize_db():
    """Create an instance of the DB if one does not already exist."""
    metadata.create_all(engine)


def _make_generic_database_entry(table, data):
    """Make a new entry in a table with an auto-incremented id."""
    with engine.connect() as conn:
        conn.execute(
            insert(
                metadata.tables[table]
            ).values(
                data
            )
        )
        conn.commit()


def _make_generic_upset_database_entry(table, data):
    """Make a new entry in a table or update an exisiting entry with same id.

    Upset is a term for adding a new entry to table or updating an existing entry
    if one already exisits. For iot_herb_garden, exisiting entries are determined
    by the id field.

    """
    with engine.connect() as conn:
        conn.execute(
            insert(
                metadata.tables[table]
            ).values(
                data
            ).on_conflict_do_update(
                index_elements=["id"],
                set_=data
            )
        )
        conn.commit()


def create_sensor(data):
    """Add or update a sensor in the database."""
    _make_generic_upset_database_entry("sensor", data)


def create_sample(data):
    """Log a sample entry in the database."""
    _make_generic_database_entry("sample", data)


def create_plant(data):
    """Add or update a plant in the database."""
    _make_generic_upset_database_entry("plant", data)


def create_watering_event(data):
    """Log a watering event in the database."""
    _make_generic_database_entry("watering_event", data)
