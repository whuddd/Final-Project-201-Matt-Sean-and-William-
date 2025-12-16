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

    # 3. Teams Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            conference TEXT,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')

    # 4. Games Table
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

    # 5. Weather Table
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

    # 6. AirQuality Table
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

    # 7. Moon_Data Table (UPDATED WITH ALL COLUMNS)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Moon_Data (
            moon_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER,
            location_id INTEGER,
            latitude REAL,
            longitude REAL,
            moon_phase TEXT,
            moon_illumination REAL,
            moonrise TEXT,          -- Added
            moonset TEXT,           -- Added
            moon_altitude REAL,     -- Added
            moon_azimuth REAL,      -- Added
            UNIQUE(date_id, location_id),
            FOREIGN KEY (date_id) REFERENCES Dates(date_id),
            FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database created with COMPLETE schema!")

if __name__ == '__main__':
    create_database()