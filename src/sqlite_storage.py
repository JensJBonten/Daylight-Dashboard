from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from .measurement import DaylightMeasurement
except ImportError:
    from measurement import DaylightMeasurement

DATABASE_FILE = Path(
    os.getenv("DAYLIGHT_DB_PATH", "data/daylight.db")
)


def _measurement_from_row(database_row: tuple) -> DaylightMeasurement:
    """Build a DaylightMeasurement from a SQLite result row."""
    return DaylightMeasurement(
        date=database_row[0],
        location_name=database_row[1],
        day_length=database_row[2],
        sunrise=database_row[3],
        sunset=database_row[4],
        daily_increase=database_row[5],
        total_increase=database_row[6],
    )


def initialize_database(
    database_file: Path = DATABASE_FILE,
) -> None:
    """Create the SQLite tables if they do not exist."""

    database_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(database_file) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS daylight_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                location_name TEXT NOT NULL,
                day_length TEXT NOT NULL,
                sunrise TEXT NOT NULL,
                sunset TEXT NOT NULL,
                daily_increase TEXT NOT NULL,
                total_increase TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'excel',
                UNIQUE(date, location_name)
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS daylight_check_ins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                location_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(date, location_name)
            )
            """
        )
        
def save_check_in(
    location_name: str,
    check_in_date: str,
    database_file: Path = DATABASE_FILE,
) -> None:
    """Registrer én innsjekking per sted og dato."""

    initialize_database(database_file)

    created_at = datetime.now(
        ZoneInfo("Europe/Oslo")
    ).isoformat()

    with sqlite3.connect(database_file) as connection:
        connection.execute(
            """
            INSERT INTO daylight_check_ins (
                date,
                location_name,
                created_at
            )
            VALUES (?, ?, ?)
            ON CONFLICT(date, location_name) DO UPDATE SET
                created_at = excluded.created_at
            """,
            (
                check_in_date,
                location_name,
                created_at,
            ),
        )


def load_check_in_dates(
    location_name: str,
    database_file: Path = DATABASE_FILE,
) -> list[str]:
    """Hent innsjekkingsdatoer for ett sted."""

    initialize_database(database_file)

    with sqlite3.connect(database_file) as connection:
        rows = connection.execute(
            """
            SELECT date
            FROM daylight_check_ins
            WHERE location_name = ?
            ORDER BY date
            """,
            (location_name,),
        ).fetchall()

    return [row[0] for row in rows]

def get_latest_check_in_measurement(
    location_name: str,
    before_date: str,
    database_file: Path = DATABASE_FILE,
) -> DaylightMeasurement | None:
    """Return the latest checked-in measurement before a date."""

    initialize_database(
        database_file
    )

    with sqlite3.connect(
        database_file
    ) as connection:
        row = connection.execute(
            """
            SELECT
                measurement.date,
                measurement.location_name,
                measurement.day_length,
                measurement.sunrise,
                measurement.sunset,
                measurement.daily_increase,
                measurement.total_increase
            FROM daylight_measurements AS measurement
            INNER JOIN daylight_check_ins AS check_in
                ON check_in.date = measurement.date
                AND check_in.location_name =
                    measurement.location_name
            WHERE check_in.location_name = ?
              AND check_in.date < ?
            ORDER BY check_in.date DESC
            LIMIT 1
            """,
            (
                location_name,
                before_date,
            ),
        ).fetchone()

    if row is None:
        return None

    return _measurement_from_row(
        row
    )


def save_measurement(
    measurement: DaylightMeasurement,
    database_file: Path = DATABASE_FILE,
    source: str = "excel",
) -> None:
    """Save one daylight measurement to SQLite.

    If the same date/location already exists, the row is updated instead of duplicated.
    """

    # Før vi lagrer, sørger vi for at databasen og tabellen finnes.
    # Dette gjør funksjonen trygg å kalle selv om databasen ikke er opprettet ennå.
    initialize_database(database_file)

    with sqlite3.connect(database_file) as connection:
        # Verdiene sendes inn separat i tuple-en under.
        # Dette er tryggere enn å bygge SQL med f-strings, fordi det beskytter mot
        # rare tegn i tekst og SQL injection.
        #
        # ON CONFLICT(date, location_name) betyr:
        # Hvis en rad med samme dato og sted allerede finnes,
        # ikke lag en duplikat. Oppdater heller den eksisterende raden.
        connection.execute(
            """
            INSERT INTO daylight_measurements (
                date,
                location_name,
                day_length,
                sunrise,
                sunset,
                daily_increase,
                total_increase,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date, location_name) DO UPDATE SET
                day_length = excluded.day_length,
                sunrise = excluded.sunrise,
                sunset = excluded.sunset,
                daily_increase = excluded.daily_increase,
                total_increase = excluded.total_increase,
                source = excluded.source
            """,
            (
                # Verdiene her matcher spørsmålstegnene i VALUES-linjen over,
                # i samme rekkefølge.
                measurement.date,
                measurement.location_name,
                measurement.day_length,
                measurement.sunrise,
                measurement.sunset,
                measurement.daily_increase,
                measurement.total_increase,
                source,
            ),
        )


def save_measurements(
    measurements: list[DaylightMeasurement],
    database_file: Path = DATABASE_FILE,
    source: str = "excel",
) -> None:
    """Save several daylight measurements to SQLite."""

    # Lagrer én og én måling.
    # Dette er enkelt å forstå og helt greit for små datasett.
    #
    # Senere kan dette optimaliseres med executemany(...),
    # men det er ikke nødvendig nå.
    for measurement in measurements:
        save_measurement(measurement, database_file=database_file, source=source)


def load_measurements(
    database_file: Path = DATABASE_FILE,
) -> list[DaylightMeasurement]:
    """Load all daylight measurements from SQLite."""

    # Sørger for at databasen og tabellen finnes før vi forsøker å lese fra den.
    # Dersom databasen er tom, returnerer SELECT bare en tom liste.
    initialize_database(database_file)

    with sqlite3.connect(database_file) as connection:
        # SELECT henter kolonner fra tabellen.
        #
        # Her hentes bare feltene som trengs for å bygge DaylightMeasurement.
        # id og source brukes ikke i modellen nå.
        database_rows = connection.execute(
            """
            SELECT
                date,
                location_name,
                day_length,
                sunrise,
                sunset,
                daily_increase,
                total_increase
            FROM daylight_measurements
            ORDER BY date
            """
        ).fetchall()

    # database_rows er en liste med tupler, eksempelvis:
    # [("2026-03-10", "Grua", "11:17:00", ...)]
    # Derfor gjøres hver tuple om til et DaylightMeasurement-objekt.
    return [_measurement_from_row(database_row) for database_row in database_rows]


def get_latest_measurement(
    database_file: Path = DATABASE_FILE,
) -> DaylightMeasurement | None:
    """Return the latest daylight measurement from SQLite, if one exists."""

    # Sørger for at databasen og tabellen finnes før den blir lest av.
    initialize_database(database_file)

    with sqlite3.connect(database_file) as connection:
        # ORDER BY date DESC sorterer nyeste dato først.
        # LIMIT 1 gjør at vi bare henter én rad.
        latest_database_row = connection.execute(
            """
            SELECT
                date,
                location_name,
                day_length,
                sunrise,
                sunset,
                daily_increase,
                total_increase
            FROM daylight_measurements
            ORDER BY date DESC
            LIMIT 1
            """
        ).fetchone()

    # fetchone() returnerer None hvis det ikke finnes noen rad.
    if latest_database_row is None:
        return None

    return _measurement_from_row(latest_database_row)


def get_previous_measurement_for_location(
    location_name: str,
    measurement_date: str,
    database_file: Path = DATABASE_FILE,
) -> DaylightMeasurement | None:
    """returnerer sist måling før valg dato for samme sted."""

    initialize_database(database_file)

    with sqlite3.connect(database_file) as connection:
        prev_database_row = connection.execute(
            """
            SELECT
                date,
                location_name,
                day_length,
                sunrise,
                sunset,
                daily_increase,
                total_increase
            FROM daylight_measurements
            WHERE location_name = ?
              AND date < ?
            ORDER BY date DESC
            LIMIT 1
            """,
            (location_name, measurement_date),
        ).fetchone()

    if prev_database_row is None:
        return None

    return _measurement_from_row(prev_database_row)


def get_first_measurement_for_location(
    location_name: str,
    database_file: Path = DATABASE_FILE,
) -> DaylightMeasurement | None:
    """Returnerer første lagrede måling for valgt sted."""

    initialize_database(database_file)

    with sqlite3.connect(database_file) as connection:
        first_database_row = connection.execute(
            """
            SELECT
                date,
                location_name,
                day_length,
                sunrise,
                sunset,
                daily_increase,
                total_increase
            FROM daylight_measurements
            WHERE location_name = ?
            ORDER BY date ASC
            LIMIT 1
            """,
            (location_name,),
        ).fetchone()

    if first_database_row is None:
        return None

    return _measurement_from_row(first_database_row)
