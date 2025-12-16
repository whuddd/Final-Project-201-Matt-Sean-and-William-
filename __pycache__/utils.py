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
    # 1. Try to find existing ID
    cursor.execute("SELECT date_id FROM Dates WHERE date_str = ?", (date_str,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # 2. Create new if not found
    cursor.execute("INSERT INTO Dates (date_str) VALUES (?)", (date_str,))
    return cursor.lastrowid

def get_or_create_location(cursor, city_name):
    """
    Get location_id for a city name, or create it if it doesn't exist.
    """
    # 1. Try to find the existing ID
    cursor.execute("SELECT location_id FROM Locations WHERE city_name = ?", (city_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        # 2. Create new location if not found
        cursor.execute("INSERT INTO Locations (city_name) VALUES (?)", (city_name,))
        return cursor.lastrowid