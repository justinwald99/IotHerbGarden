"""Utility functions for interacting with the database."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.sqlite import insert


def create_db(engine, metadata):
    """Create an instance of the DB if one does not already exist."""
    Table(
        "sensor",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("type", String, nullable=False),
        Column("name", String, nullable=False),
        Column("unit", String, nullable=False),
        Column("sample_gap", Integer, nullable=False)
    )

    Table(
        "sample",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("sensor_id", ForeignKey("sensor.id"), nullable=False),
        Column("timestamp", TIMESTAMP, nullable=False),
        Column("value", Integer, nullable=False)
    )

    Table(
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

    Table(
        "watering_event",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("plant_id", ForeignKey("plant.id"), nullable=False),
        Column("timestamp", TIMESTAMP, nullable=False),
        Column("duration", Integer, nullable=False)
    )

    metadata.create_all(engine)


def _make_generic_database_entry(engine, metadata, table, data):
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


def _make_generic_upset_database_entry(engine, metadata, table, data):
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


def create_sensor(engine, metadata, data):
    """Add or update a sensor in the database."""
    _make_generic_upset_database_entry(engine, metadata, "sensor", data)


def create_sample(engine, metadata, data):
    """Log a sample entry in the database."""
    _make_generic_database_entry(engine, metadata, "sample", data)


def create_plant(engine, metadata, data):
    """Add or update a plant in the database."""
    _make_generic_upset_database_entry(engine, metadata, "plant", data)


def create_watering_event(engine, metadata, data):
    """Log a watering event in the database."""
    _make_generic_database_entry(engine, metadata, "watering_event", data)
