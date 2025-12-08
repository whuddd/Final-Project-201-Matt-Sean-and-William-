import sqlite3

def create_database():
    """
    Create all tables for the project
    Run this ONCE at the beginning
    """
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # Table 1: Teams (avoids duplicate team names)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            conference TEXT,
            stadium_city TEXT
        )
    ''')
    
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
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == '__main__':
    create_database()