# create_database.py
# Run this ONCE at the start to create your database

import sqlite3

def create_database():
    """
    Create all tables for the project
    """
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Table 1: Teams (avoids duplicate team names)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            conference TEXT,
            stadium_city TEXT
        )
    ''')
    print("  ✓ Teams table created")
    
    # Table 2: Games (references Teams table)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            game_id INTEGER PRIMARY KEY,
            game_date TEXT NOT NULL,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            stadium_city TEXT,
            FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
            FOREIGN KEY (away_team_id) REFERENCES Teams(team_id)
        )
    ''')
    print("  ✓ Games table created")
    
    # Table 3: Weather Data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Weather (
            weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location TEXT NOT NULL,
            temperature REAL,
            wind_speed REAL,
            humidity REAL,
            precipitation REAL,
            weather_code INTEGER
        )
    ''')
    print("  ✓ Weather table created")
    
    # Table 4: Air Quality Data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AirQuality (
            measure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location TEXT NOT NULL,
            pollutant_type TEXT,
            pollutant_value REAL,
            unit TEXT
        )
    ''')
    print("  ✓ AirQuality table created")
    
    # Table 5: UV Data (BONUS API)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UV_Data (
            uv_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            uv_index REAL,
            uv_max REAL,
            uv_max_time TEXT,
            ozone REAL,
            safe_exposure_time INTEGER
        )
    ''')
    print("  ✓ UV_Data table created")
    
    # Table 6: Moon Phase Data (BONUS API #2) - NEW!
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Moon_Data (
            moon_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            moon_phase TEXT,
            moon_illumination REAL,
            moonrise TEXT,
            moonset TEXT,
            moon_altitude REAL,
            moon_azimuth REAL,
            UNIQUE(game_date, location)
        )
    ''')
    print("  ✓ Moon_Data table created")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database created successfully!")
    print("   Tables: Teams, Games, Weather, AirQuality, UV_Data, Moon_Data")

if __name__ == '__main__':
    create_database()