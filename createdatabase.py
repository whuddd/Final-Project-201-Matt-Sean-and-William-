# createdatabase.py
import sqlite3

def create_database():
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # 1. Dates Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dates (
            date_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT UNIQUE NOT NULL
        )
    ''')

    # 2. Locations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT UNIQUE NOT NULL
        )
    ''')

    # 3. MoonPhases Table (NEW!)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MoonPhases (
            phase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase_name TEXT UNIQUE NOT NULL
        )
    ''')

    # 4. Teams Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            conference TEXT,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 5. Games Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            game_id INTEGER PRIMARY KEY,
            date_id INTEGER,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            location_id INTEGER, 
            attendance INTEGER,
            kickoff_time TEXT,
            FOREIGN KEY (date_id) REFERENCES Dates(date_id),
            FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
            FOREIGN KEY (away_team_id) REFERENCES Teams(team_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 6. Weather Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Weather (
            weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER,
            location_id INTEGER,
            temperature REAL,
            wind_speed REAL,
            humidity REAL,
            precipitation REAL,
            weather_code INTEGER,
            FOREIGN KEY (date_id) REFERENCES Dates(date_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 7. AirQuality Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AirQuality (
            measure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER,
            location_id INTEGER,
            pollutant_type TEXT,
            pollutant_value REAL,
            unit TEXT,
            FOREIGN KEY (date_id) REFERENCES Dates(date_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 8. Moon_Data Table (NORMALIZED & SIMPLIFIED)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Moon_Data (
            moon_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER,
            location_id INTEGER,
            phase_id INTEGER,             -- CHANGED: Uses ID now
            latitude REAL,
            longitude REAL,
            moon_illumination REAL,
            UNIQUE(date_id, location_id),
            FOREIGN KEY (date_id) REFERENCES Dates(date_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id),
            FOREIGN KEY (phase_id) REFERENCES MoonPhases(phase_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database created with NORMALIZED Moon Phases!")

if __name__ == '__main__':
    create_database()