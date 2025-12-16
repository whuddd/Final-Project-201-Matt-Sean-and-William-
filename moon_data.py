# moon_data.py
import sqlite3
import requests
from datetime import datetime, timedelta
import time
# IMPORT ALL 3 HELPERS
from utils import get_or_create_date, get_or_create_location, get_or_create_moon_phase

# Cities matching football/weather/AQ/UV data (25 cities)
CITIES = {
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
    'Gainesville': {'lat': 29.6516, 'lon': -82.3248},
    'Tallahassee': {'lat': 30.4383, 'lon': -84.2807},
    'Blacksburg': {'lat': 37.2296, 'lon': -80.4139},
    'Clemson': {'lat': 34.6834, 'lon': -82.8374},
    'Atlanta': {'lat': 33.7756, 'lon': -84.3963},
}

IPGEOLOCATION_KEY = "2313acdb637c40db840995cd5da683ed"

def get_moon_phase_from_api(lat, lon, date, city):
    url = "https://api.ipgeolocation.io/v2/astronomy"
    params = {
        'apiKey': IPGEOLOCATION_KEY,
        'location': f"{city}, US",
        'date': date
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def show_database_stats():
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM Moon_Data")
        total = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        print("Table not found or empty.")
        conn.close()
        return 0
    
    # Joins needed to verify data
    cursor.execute("""
        SELECT l.city_name, COUNT(*) 
        FROM Moon_Data m
        JOIN Locations l ON m.location_id = l.location_id
        GROUP BY l.city_name 
        ORDER BY COUNT(*) DESC
    """)
    by_location = cursor.fetchall()
    
    print(f"\nTotal moon records: {total}")
    conn.close()
    return total

def store_moon_data():
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Moon_Data")
        actual_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        actual_count = 0
    
    # Check existing (Needs 3-way join now!)
    try:
        cursor.execute("""
            SELECT d.date_str, l.city_name 
            FROM Moon_Data m 
            JOIN Locations l ON m.location_id = l.location_id
            JOIN Dates d ON m.date_id = d.date_id
        """)
        existing = set(cursor.fetchall())
    except sqlite3.OperationalError:
        existing = set()
    
    print(f"\nMOON PHASE DATA COLLECTION (Normalized)")
    print(f"Current records: {actual_count}")
    
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
    
    print(f"New combinations: {len(all_combinations)}")
    
    stored_count = 0
    
    for date, city, coords in all_combinations:
        if stored_count >= 25:
            print(f"\n✓ Reached 25-item limit")
            break
        
        print(f"[{stored_count + 1}/25] {city} on {date}...", end=" ")
        
        moon_data = get_moon_phase_from_api(coords['lat'], coords['lon'], date, city)
        
        if moon_data and 'astronomy' in moon_data:
            astronomy = moon_data['astronomy']
            moon_phase_str = astronomy.get('moon_phase', 'Unknown')
            moon_illumination = astronomy.get('moon_illumination_percentage')
            location_data = moon_data.get('location', {})
            returned_lat = location_data.get('latitude')
            returned_lon = location_data.get('longitude')
            
            if isinstance(moon_illumination, str):
                try: moon_illumination = float(moon_illumination)
                except: moon_illumination = None
            
            try:
                # 1. Get IDs for Location and Date
                loc_id = get_or_create_location(cursor, city)
                date_id = get_or_create_date(cursor, date)

                # 2. Get ID for Moon Phase (NEW NORMALIZATION)
                phase_id = get_or_create_moon_phase(cursor, moon_phase_str)

                # 3. Insert IDs
                cursor.execute('''
                    INSERT INTO Moon_Data 
                    (date_id, location_id, phase_id, latitude, longitude, moon_illumination)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (date_id, loc_id, phase_id, returned_lat, returned_lon, moon_illumination))
                
                stored_count += 1
                illum_str = f"{moon_illumination:.1f}%" if moon_illumination else "N/A"
                print(f"✓ {moon_phase_str}, {illum_str}")
                
            except sqlite3.IntegrityError:
                print(f"✗ Duplicate")
        else:
            print(f"✗ No data")
        
        time.sleep(1)
    
    conn.commit()
    conn.close()
    show_database_stats()

if __name__ == '__main__':
    store_moon_data()