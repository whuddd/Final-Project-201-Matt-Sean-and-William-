# moon_data.py
# BONUS API #2 - Moon Phase Data Collection using IP Geolocation
# Run this 4+ times to collect 100+ moon phase records

import sqlite3
import requests
from datetime import datetime, timedelta
import time

# Cities matching football/weather/AQ/UV data (25 cities)
CITIES = {
    # Original 10 cities
    'Ann Arbor': {'lat': 42.2808, 'lon': -83.7430},
    'Columbus': {'lat': 40.0012, 'lon': -83.0302},
    'State College': {'lat': 40.7982, 'lon': -77.8599},
    'Madison': {'lat': 43.0731, 'lon': -89.4012},
    'Iowa City': {'lat': 41.6611, 'lon': -91.5302},
    'Eugene': {'lat': 44.0521, 'lon': -123.0868},
    'Austin': {'lat': 30.2849, 'lon': -97.7341},
    'Tuscaloosa': {'lat': 33.2098, 'lon': -87.5692},
    'Athens': {'lat': 33.9519, 'lon': -83.3576},
    'Baton Rouge': {'lat': 30.4515, 'lon': -91.1871},

    # Big Ten additions (11-15)
    'East Lansing': {'lat': 42.7370, 'lon': -84.4839},
    'Lincoln': {'lat': 40.8136, 'lon': -96.7026},
    'Champaign': {'lat': 40.1164, 'lon': -88.2434},
    'West Lafayette': {'lat': 40.4259, 'lon': -86.9081},
    'Bloomington': {'lat': 39.1653, 'lon': -86.5264},

    # SEC/Big 12 additions (16-20)
    'Knoxville': {'lat': 35.9606, 'lon': -83.9207},
    'Auburn': {'lat': 32.5990, 'lon': -85.4808},
    'College Station': {'lat': 30.6280, 'lon': -96.3344},
    'Starkville': {'lat': 33.4504, 'lon': -88.8184},
    'Columbia': {'lat': 34.0007, 'lon': -81.0348},

    # Additional major programs (21-25)
    'Gainesville': {'lat': 29.6516, 'lon': -82.3248},
    'Tallahassee': {'lat': 30.4383, 'lon': -84.2807},
    'Blacksburg': {'lat': 37.2296, 'lon': -80.4139},
    'Clemson': {'lat': 34.6834, 'lon': -82.8374},
    'Atlanta': {'lat': 33.7756, 'lon': -84.3963},
}

# Your IPGeolocation API key
IPGEOLOCATION_KEY = "2313acdb637c40db840995cd5da683ed"


def get_moon_phase_from_api(lat, lon, date, city):
    """
    Get moon phase data from IP Geolocation Astronomy API.
    """
    url = "https://api.ipgeolocation.io/v2/astronomy"
    location = f"{city}, US"
    params = {
        "apiKey": IPGEOLOCATION_KEY,
        "location": location,
        "date": date,  # YYYY-MM-DD
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        print(f"    Error {resp.status_code}")
        return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None


def create_moon_table():
    """
    Create Moon_Data table if it doesn't exist.
    Schema matches the existing simple version (no moonrise, etc.).
    """
    conn = sqlite3.connect("football_weather.db")
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Moon_Data (
            moon_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location_id INTEGER,
            latitude REAL,
            longitude REAL,
            moon_phase TEXT,
            moon_illumination REAL,
            UNIQUE(game_date, location_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
        """
    )

    conn.commit()
    conn.close()
    print("✅ Moon_Data table created/verified")


def show_database_stats():
    """Show current Moon_Data statistics."""
    conn = sqlite3.connect("football_weather.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Moon_Data")
    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT l.city_name, COUNT(*)
        FROM Moon_Data m
        JOIN Locations l ON m.location_id = l.location_id
        GROUP BY l.city_name
        ORDER BY COUNT(*) DESC
        """
    )
    by_location = cur.fetchall()

    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    print(f"Total moon records: {total}")
    print("\nRecords by location:")
    for city_name, count in by_location:
        print(f"  {city_name}: {count}")

    conn.close()
    return total


def get_or_create_location(cur, city_name):
    """Return location_id for a city, creating it if needed."""
    cur.execute(
        "SELECT location_id FROM Locations WHERE city_name = ?",
        (city_name,),
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute("INSERT INTO Locations (city_name) VALUES (?)", (city_name,))
    return cur.lastrowid


def store_moon_data():
    """Store up to 25 moon phase records per run."""
    create_moon_table()

    conn = sqlite3.connect("football_weather.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Moon_Data")
    actual_count = cur.fetchone()[0]

    # Existing (game_date, city) combos
    try:
        cur.execute(
            """
            SELECT m.game_date, l.city_name
            FROM Moon_Data m
            JOIN Locations l ON m.location_id = l.location_id
            """
        )
        existing = set(cur.fetchall())
    except sqlite3.OperationalError:
        existing = set()

    print("\n" + "=" * 60)
    print("MOON PHASE DATA COLLECTION")
    print("=" * 60)
    print(f"Current records: {actual_count}")

    # All Saturdays between 2024‑09‑01 and 2024‑11‑30
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 11, 30)
    saturdays = []
    cur_date = start_date
    while cur_date <= end_date:
        if cur_date.weekday() == 5:  # Saturday
            saturdays.append(cur_date)
        cur_date += timedelta(days=1)

    all_combos = []
    for city, coords in CITIES.items():
        for d in saturdays:
            date_str = d.strftime("%Y-%m-%d")
            if (date_str, city) not in existing:
                all_combos.append((date_str, city, coords))

    print(f"New combinations available: {len(all_combos)}")

    stored = 0

    for date_str, city, coords in all_combos:
        if stored >= 25:
            print("\n✓ Reached 25-item limit")
            break

        print(f"[{stored + 1}/25] {city} on {date_str}...", end=" ")

        data = get_moon_phase_from_api(coords["lat"], coords["lon"], date_str, city)

        if data and "astronomy" in data:
            astronomy = data["astronomy"]
            moon_phase = astronomy.get("moon_phase", "Unknown")
            moon_illumination = astronomy.get("moon_illumination_percentage")

            loc_info = data.get("location", {})
            returned_lat = loc_info.get("latitude")
            returned_lon = loc_info.get("longitude")

            if isinstance(moon_illumination, str):
                try:
                    moon_illumination = float(moon_illumination)
                except Exception:
                    moon_illumination = None

            try:
                loc_id = get_or_create_location(cur, city)

                cur.execute(
                    """
                    INSERT INTO Moon_Data
                        (game_date,
                         location_id,
                         latitude,
                         longitude,
                         moon_phase,
                         moon_illumination)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        date_str,
                        loc_id,
                        returned_lat,
                        returned_lon,
                        moon_phase,
                        moon_illumination,
                    ),
                )

                stored += 1
                illum_str = (
                    f"{moon_illumination:.1f}%"
                    if moon_illumination is not None
                    else "N/A"
                )
                print(f"✓ {moon_phase}, {illum_str}")
            except sqlite3.IntegrityError:
                print("✗ Duplicate")
        else:
            print("✗ No data")

        time.sleep(1)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM Moon_Data")
    final_count = cur.fetchone()[0]
    conn.close()

    print("\n" + "=" * 60)
    print(f"Added: {stored}")
    print(f"Total now: {final_count}")
    show_database_stats()


if __name__ == "__main__":
    store_moon_data()
