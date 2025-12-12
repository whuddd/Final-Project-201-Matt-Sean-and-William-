# air_quality_data.py
# Sean - Air Quality Data Collection using Open-Meteo
# Run this 4+ times to collect 100+ air quality records
# NO API KEY NEEDED!

import sqlite3
import requests
from datetime import datetime, timedelta
import time

# Cities matching football/weather/UV/Moon data (25 cities)
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

def get_air_quality_from_api(lat, lon, date):
    """
    Get air quality data from Open-Meteo Air Quality API
    Returns hourly data for the specified date
    NO API KEY NEEDED!
    """
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': date,
        'end_date': date,
        'hourly': 'us_aqi,pm2_5,pm10',
        'timezone': 'auto'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                print(f"    API Error: {data.get('reason', 'Unknown')}")
                return None
            
            return data
        else:
            print(f"    HTTP Error {response.status_code}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def show_database_stats():
    """
    Show current database statistics
    """
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # Total count (Make sure your table is named 'AirQuality')
    cursor.execute("SELECT COUNT(*) FROM AirQuality")
    total = cursor.fetchone()[0]
    
    # Count by location (CORRECTED: Joins AirQuality and Locations tables)
    cursor.execute("""
        SELECT l.city_name, COUNT(*) 
        FROM AirQuality a
        JOIN Locations l ON a.location_id = l.location_id
        GROUP BY l.city_name 
        ORDER BY COUNT(*) DESC
    """)
    by_location = cursor.fetchall()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total air quality records: {total}")
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

def store_air_quality_data():
    """Store up to 25 air quality records per run"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM AirQuality")
    actual_count = cursor.fetchone()[0]
    
    # Check existing (Joined with Locations)
    try:
        cursor.execute("""
            SELECT a.game_date, l.city_name 
            FROM AirQuality a 
            JOIN Locations l ON a.location_id = l.location_id
        """)
        existing = set(cursor.fetchall())
    except sqlite3.OperationalError:
        existing = set()
    
    print(f"\n{'='*60}")
    print(f"AIR QUALITY DATA COLLECTION")
    print(f"{'='*60}")
    print(f"Current records: {actual_count}")
    
    # Generate Saturdays
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 11, 30)
    saturdays = []
    current = start_date
    while current <= end_date:
        if current.weekday() == 5:
            saturdays.append(current)
        current += timedelta(days=1)
    
    all_combinations = []
    for city, coords in CITIES.items():
        for saturday in saturdays:
            date_str = saturday.strftime('%Y-%m-%d')
            if (date_str, city) not in existing:
                all_combinations.append((date_str, city, coords))
    
    print(f"New combinations available: {len(all_combinations)}")
    
    stored_count = 0
    
    for date, city, coords in all_combinations:
        if stored_count >= 25:
            print(f"\n✓ Reached 25-item limit")
            break
        
        print(f"[{stored_count + 1}/25] {city} on {date}...", end=" ")
        
        aq_data = get_air_quality_from_api(coords['lat'], coords['lon'], date)
        
        if aq_data and 'hourly' in aq_data:
            hourly = aq_data['hourly']
            times = hourly.get('time', [])
            us_aqi = hourly.get('us_aqi', [])
            
            # Average AQI for hours 12-15
            game_aqi_values = []
            for i, t in enumerate(times):
                hour = int(t.split('T')[1].split(':')[0])
                if 12 <= hour <= 15:
                    if us_aqi[i] is not None:
                        game_aqi_values.append(us_aqi[i])
            
            if game_aqi_values:
                avg_aqi = sum(game_aqi_values) / len(game_aqi_values)
                
                try:
                    # 1. Get Location ID
                    loc_id = get_or_create_location(cursor, city)

                    # 2. Insert using location_id
                    cursor.execute('''
                        INSERT INTO AirQuality 
                        (game_date, location_id, pollutant_type, pollutant_value, unit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (date, loc_id, 'US_AQI', avg_aqi, 'AQI'))
                    
                    stored_count += 1
                    print(f"✓ AQI: {avg_aqi:.1f}")
                    
                except sqlite3.IntegrityError:
                    print(f"✗ Duplicate")
            else:
                print(f"✗ No valid data")
        else:
            print(f"✗ No data")
        
        time.sleep(0.3)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM AirQuality")
    final_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Added: {stored_count}")
    print(f"Total now: {final_count}")
    show_database_stats()

if __name__ == '__main__':
    store_air_quality_data()