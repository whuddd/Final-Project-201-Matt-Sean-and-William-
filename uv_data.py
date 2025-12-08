# moon_data.py
# BONUS API #2 - Moon Phase Data Collection using IP Geolocation
# Run this 4+ times to collect 100+ moon phase records

import sqlite3
import requests
from datetime import datetime, timedelta
import time

# Cities matching football/weather/AQ/UV data (25 cities)
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

# Add this to your config.py
IPGEOLOCATION_KEY = "2313acdb637c40db840995cd5da683ed"

def get_moon_phase_from_api(lat, lon, date, city):
    """
    Get moon phase data from IP Geolocation Astronomy API
    URL: https://api.ipgeolocation.io/v2/astronomy?apiKey={key}&location={location}&date={date}
    """
    url = "https://api.ipgeolocation.io/v2/astronomy"
    
    # Format location as "City, State" or just city name
    location = f"{city}, US"
    
    params = {
        'apiKey': IPGEOLOCATION_KEY,
        'location': location,
        'date': date  # Format: YYYY-MM-DD
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"    Error {response.status_code}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def create_moon_table():
    """Create moon phase table if it doesn't exist"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    print("✅ Moon_Data table created/verified")

def show_database_stats():
    """Show current database statistics"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Moon_Data")
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT location, COUNT(*) 
        FROM Moon_Data 
        GROUP BY location 
        ORDER BY COUNT(*) DESC
    """)
    by_location = cursor.fetchall()
    
    # Count by moon phase
    cursor.execute("""
        SELECT moon_phase, COUNT(*) 
        FROM Moon_Data 
        GROUP BY moon_phase 
        ORDER BY COUNT(*) DESC
    """)
    by_phase = cursor.fetchall()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total moon records: {total}")
    
    if by_location:
        print("\nRecords by location:")
        for location, count in by_location[:5]:  # Top 5
            print(f"  {location}: {count}")
    
    if by_phase:
        print("\nRecords by moon phase:")
        for phase, count in by_phase:
            print(f"  {phase}: {count}")
    
    conn.close()
    return total

def store_moon_data():
    """Store up to 25 moon phase records per run"""
    
    # Make sure table exists
    create_moon_table()
    
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Moon_Data")
    actual_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT game_date, location FROM Moon_Data")
    existing = set(cursor.fetchall())
    
    print(f"\n{'='*60}")
    print(f"MOON PHASE DATA COLLECTION - 2024 SEASON (BONUS API #2)")
    print(f"{'='*60}")
    print(f"Current records: {actual_count}")
    print(f"Total cities: {len(CITIES)}")
    print(f"Using: IP Geolocation Astronomy API")
    print(f"{'='*60}\n")
    
    # Generate Saturdays during football season (Sep-Nov 2024)
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 11, 30)
    
    saturdays = []
    current = start_date
    while current <= end_date:
        if current.weekday() == 5:
            saturdays.append(current)
        current += timedelta(days=1)
    
    print(f"Total Saturdays: {len(saturdays)}")
    print(f"Max combinations: {len(saturdays) * len(CITIES)}")
    
    # Create list of all combinations
    all_combinations = []
    for city, coords in CITIES.items():
        for saturday in saturdays:
            date_str = saturday.strftime('%Y-%m-%d')
            if (date_str, city) not in existing:
                all_combinations.append((date_str, city, coords))
    
    print(f"New combinations available: {len(all_combinations)}")
    print(f"{'='*60}\n")
    
    if len(all_combinations) == 0:
        print("⚠️  No new data to collect!")
        show_database_stats()
        conn.close()
        return
    
    stored_count = 0
    failed_count = 0
    
    # Collect data
    for date, city, coords in all_combinations:
        if stored_count >= 25:
            print(f"\n✓ Reached 25-item limit")
            break
        
        print(f"[{stored_count + 1}/25] {city} on {date}...", end=" ")
        
        moon_data = get_moon_phase_from_api(coords['lat'], coords['lon'], date, city)
        
        if moon_data and 'astronomy' in moon_data:
            astronomy = moon_data['astronomy']
            
            # Extract moon phase data
            moon_phase = astronomy.get('moon_phase', 'Unknown')
            moon_illumination = astronomy.get('moon_illumination_percentage')
            moonrise = astronomy.get('moonrise', '-:-')
            moonset = astronomy.get('moonset', '-:-')
            moon_altitude = astronomy.get('moon_altitude')
            moon_azimuth = astronomy.get('moon_azimuth')
            
            # Get location data
            location_data = moon_data.get('location', {})
            returned_lat = location_data.get('latitude')
            returned_lon = location_data.get('longitude')
            
            # Convert illumination from string to float if needed
            if isinstance(moon_illumination, str):
                try:
                    moon_illumination = float(moon_illumination)
                except:
                    moon_illumination = None
            
            try:
                cursor.execute('''
                    INSERT INTO Moon_Data 
                    (game_date, location, latitude, longitude, moon_phase, 
                     moon_illumination, moonrise, moonset, moon_altitude, moon_azimuth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date, city, returned_lat, returned_lon, moon_phase,
                      moon_illumination, moonrise, moonset, moon_altitude, moon_azimuth))
                
                stored_count += 1
                illum_str = f"{moon_illumination:.1f}%" if moon_illumination else "N/A"
                print(f"✓ {moon_phase}, {illum_str}")
                
            except sqlite3.IntegrityError:
                print(f"✗ Duplicate")
                failed_count += 1
        else:
            print(f"✗ No data")
            failed_count += 1
        
        # Delay between requests to be respectful
        time.sleep(1)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM Moon_Data")
    final_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"COLLECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Added: {stored_count}")
    print(f"Failed: {failed_count}")
    print(f"Total now: {final_count}")
    
    remaining = len(all_combinations) - stored_count
    if remaining > 0:
        runs_needed = (remaining // 25) + (1 if remaining % 25 else 0)
        print(f"Runs needed: {runs_needed}")
    else:
        print("✅ All data collected!")
    
    print(f"{'='*60}\n")
    show_database_stats()

if __name__ == '__main__':
    store_moon_data()