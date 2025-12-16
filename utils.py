# utils.py
import sqlite3

def connect_db():
    """Connect to the database"""
    return sqlite3.connect('football_weather.db')

def ensure_outputs_dir():
    """Make sure the outputs directory exists"""
    import os
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

def get_or_create_date(cursor, date_str):
    """
    Takes a date string (e.g., '2024-09-01').
    Returns its integer ID from the Dates table.
    """
    cursor.execute("SELECT date_id FROM Dates WHERE date_str = ?", (date_str,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO Dates (date_str) VALUES (?)", (date_str,))
    return cursor.lastrowid

def get_or_create_location(cursor, city_name):
    """
    Get location_id for a city name, or create it if it doesn't exist.
    """
    cursor.execute("SELECT location_id FROM Locations WHERE city_name = ?", (city_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO Locations (city_name) VALUES (?)", (city_name,))
    return cursor.lastrowid

# --- NEW HELPER FOR MOON PHASES ---
def get_or_create_moon_phase(cursor, phase_name):
    """
    Get phase_id for a moon phase name, or create it if it doesn't exist.
    """
    cursor.execute("SELECT phase_id FROM MoonPhases WHERE phase_name = ?", (phase_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO MoonPhases (phase_name) VALUES (?)", (phase_name,))
    return cursor.lastrowid