# weather_data.py
# Matt - Weather Data Collection
# Run this 4+ times to collect 100+ weather records

import sqlite3
import requests
from datetime import datetime, timedelta
import time

# Stadium coordinates 
STADIUMS = {
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
    'East Lansing': {'lat': 42.7370, 'lon': -84.4839},
    'Lincoln': {'lat': 40.8136, 'lon': -96.7026},
    'Champaign': {'lat': 40.1164, 'lon': -88.2434},
    'West Lafayette': {'lat': 40.4259, 'lon': -86.9081},
    'Bloomington': {'lat': 39.1653, 'lon': -86.5264},
    'Knoxville': {'lat': 35.9606, 'lon': -83.9207},
    'Auburn': {'lat': 32.5990, 'lon': -85.4808},
    'College Station': {'lat': 30.6280, 'lon': -96.3344},
    'Starkville': {'lat': 33.4504, 'lon': -88.8184},
    'Columbia': {'lat': 34.0007, 'lon': -81.0348},
    'Gainesville': {'lat': 29.6516, 'lon': -82.3248},  # Florida
    'Tallahassee': {'lat': 30.4383, 'lon': -84.2807},  # Florida State
    'Blacksburg': {'lat': 37.2296, 'lon': -80.4139},  # Virginia Tech
    'Clemson': {'lat': 34.6834, 'lon': -82.8374},  # Clemson
    'Atlanta': {'lat': 33.7756, 'lon': -84.3963},  # Georgia Tech
}

def get_weather_from_api(lat, lon, date):
    """
    Get HISTORICAL weather data from Open-Meteo Archive API
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': date,
        'end_date': date,
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code',
        'temperature_unit': 'fahrenheit',
        'wind_speed_unit': 'mph',
        'precipitation_unit': 'inch',
        'timezone': 'America/New_York'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            hourly = data.get('hourly', {})
            
            if not hourly or 'temperature_2m' not in hourly:
                return None
            
            # Get game time data (1 PM = hour 13)
            game_hour_index = 13
            if len(hourly['temperature_2m']) <= game_hour_index:
                game_hour_index = len(hourly['temperature_2m']) - 1
            
            return {
                'temperature': hourly['temperature_2m'][game_hour_index],
                'humidity': hourly['relative_humidity_2m'][game_hour_index],
                'precipitation': hourly['precipitation'][game_hour_index],
                'wind_speed': hourly['wind_speed_10m'][game_hour_index],
                'weather_code': hourly['weather_code'][game_hour_index]
            }
        else:
            return None
    except Exception as e:
        return None

def show_database_stats():
    """
    Show current database statistics
    """
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM Weather")
    total = cursor.fetchone()[0]
    
    # Count by location (CORRECTED: Joins Weather and Locations tables)
    cursor.execute("""
        SELECT l.city_name, COUNT(*) 
        FROM Weather w
        JOIN Locations l ON w.location_id = l.location_id
        GROUP BY l.city_name 
        ORDER BY COUNT(*) DESC
    """)
    by_location = cursor.fetchall()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total weather records: {total}")
    print("\nRecords by location:")
    for location, count in by_location:
        print(f"  {location}: {count}")
    
    conn.close()
    return total

def get_or_create_location(cursor, city_name):
    """Get location_id or create new location"""
    cursor.execute("SELECT location_id FROM Locations WHERE city_name = ?", (city_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO Locations (city_name) VALUES (?)", (city_name,))
    return cursor.lastrowid

def store_weather_data():
    """
    Store up to 25 weather records per run
    """
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # Verify actual count
    cursor.execute("SELECT COUNT(*) FROM Weather")
    actual_count = cursor.fetchone()[0]
    
    # Check existing records (Need to join with Locations to check by name)
    # Note: If the DB is empty, this returns nothing, which is fine.
    try:
        cursor.execute("""
            SELECT w.game_date, l.city_name 
            FROM Weather w 
            JOIN Locations l ON w.location_id = l.location_id
        """)
        existing = set(cursor.fetchall())
    except sqlite3.OperationalError:
        # Handle case where table might be empty or join fails initially
        existing = set()
    
    print(f"\n{'='*60}")
    print(f"WEATHER DATA COLLECTION - 2024 SEASON")
    print(f"{'='*60}")
    print(f"Current records in database: {actual_count}")
    print(f"Total cities: {len(STADIUMS)} cities")
    print(f"{'='*60}\n")
    
    # Generate Saturdays during football season (Sep-Nov 2024)
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 11, 30)
    
    saturdays = []
    current = start_date
    while current <= end_date:
        if current.weekday() == 5:  # Saturday
            saturdays.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    # CREATE LIST OF ALL POSSIBLE COMBINATIONS
    all_combinations = []
    for city, coords in STADIUMS.items():
        for date in saturdays:
            if (date, city) not in existing:
                all_combinations.append((date, city, coords))
    
    print(f"New combinations available to collect: {len(all_combinations)}")
    print(f"{'='*60}\n")
    
    if len(all_combinations) == 0:
        print("⚠️  No new data to collect!")
        show_database_stats()
        conn.close()
        return
    
    stored_count = 0
    failed_count = 0
    
    # Collect data from the list of new combinations
    for date, city, coords in all_combinations:
        if stored_count >= 25:
            print(f"\n✓ Reached 25-item limit for this run")
            break
        
        print(f"[{stored_count + 1}/25] Fetching {city} on {date}...", end=" ")
        weather = get_weather_from_api(coords['lat'], coords['lon'], date)
        
        if weather:
            try:
                # 1. Get the Location ID
                loc_id = get_or_create_location(cursor, city)

                # 2. Insert using location_id instead of city string
                cursor.execute('''
                    INSERT INTO Weather 
                    (game_date, location_id, temperature, wind_speed, 
                     humidity, precipitation, weather_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (date, loc_id, weather['temperature'], weather['wind_speed'],
                      weather['humidity'], weather['precipitation'], 
                      weather['weather_code']))
                
                stored_count += 1
                print(f"✓ {weather['temperature']:.1f}°F")
            except sqlite3.IntegrityError:
                print(f"✗ Duplicate (skipping)")
                failed_count += 1
        else:
            print(f"✗ No data")
            failed_count += 1
        
        time.sleep(0.5)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM Weather")
    final_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"COLLECTION COMPLETE")
    print(f"{'='*60}")
    print(f"New records added: {stored_count}")
    print(f"New total: {final_count}")
    
    if final_count < 100:
        runs_needed = ((100 - final_count) // 25) + 1
        print(f"Need {runs_needed} more runs")
    else:
        print("✅ 100+ records collected!")
    print(f"{'='*60}\n")
    show_database_stats()

if __name__ == '__main__':
    store_weather_data()