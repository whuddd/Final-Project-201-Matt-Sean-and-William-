# create_database.py
# Run this ONCE at the start to create your database

import sqlite3

def create_database():
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # 1. NEW: Locations Table (The "Master" list of cities)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT UNIQUE NOT NULL
        )
    ''')

    # 2. Teams: Change stadium_city (Text) to location_id (Integer)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            conference TEXT,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 3. Games: Change stadium_city (Text) to location_id (Integer)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            game_id INTEGER PRIMARY KEY,
            game_date TEXT NOT NULL,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            location_id INTEGER, 
            attendance INTEGER,
            kickoff_time TEXT,
            FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
            FOREIGN KEY (away_team_id) REFERENCES Teams(team_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 4. Weather: Change location (Text) to location_id (Integer)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Weather (
            weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location_id INTEGER,
            temperature REAL,
            wind_speed REAL,
            humidity REAL,
            precipitation REAL,
            weather_code INTEGER,
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 5. AirQuality: Change location (Text) to location_id (Integer)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AirQuality (
            measure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            location_id INTEGER,
            pollutant_type TEXT,
            pollutant_value REAL,
            unit TEXT,
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 6. Moon_Data: Change location (Text) to location_id (Integer)
    cursor.execute('''
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
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()