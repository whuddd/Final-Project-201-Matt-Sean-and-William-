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
    """Show current database statistics"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM AirQuality")
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT location, COUNT(*) 
        FROM AirQuality 
        GROUP BY location 
        ORDER BY COUNT(*) DESC
    """)
    by_location = cursor.fetchall()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total air quality records: {total}")
    
    if by_location:
        print("\nRecords by location:")
        for location, count in by_location[:10]:  # Top 10
            print(f"  {location}: {count}")
    
    conn.close()
    return total

def store_air_quality_data():
    """Store up to 25 air quality records per run"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM AirQuality")
    actual_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT game_date, location FROM AirQuality")
    existing = set(cursor.fetchall())
    
    print(f"\n{'='*60}")
    print(f"AIR QUALITY DATA COLLECTION - 2024 SEASON")
    print(f"{'='*60}")
    print(f"Current records: {actual_count}")
    print(f"Total cities: {len(CITIES)}")
    print(f"Using: Open-Meteo Air Quality API (NO KEY NEEDED!)")
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
        
        aq_data = get_air_quality_from_api(coords['lat'], coords['lon'], date)
        
        if aq_data and 'hourly' in aq_data:
            hourly = aq_data['hourly']
            times = hourly.get('time', [])
            us_aqi = hourly.get('us_aqi', [])
            pm25 = hourly.get('pm2_5', [])
            pm10 = hourly.get('pm10', [])
            
            # Calculate average for the day (game time around 1 PM = hour 13)
            # Get data around game time (hours 12-15)
            game_hours = []
            for i, t in enumerate(times):
                hour = int(t.split('T')[1].split(':')[0])
                if 12 <= hour <= 15:
                    if us_aqi[i] is not None:
                        game_hours.append({
                            'aqi': us_aqi[i],
                            'pm25': pm25[i],
                            'pm10': pm10[i]
                        })
            
            if game_hours:
                # Average the game-time hours
                avg_aqi = sum(h['aqi'] for h in game_hours) / len(game_hours)
                avg_pm25 = sum(h['pm25'] for h in game_hours if h['pm25'] is not None) / len([h for h in game_hours if h['pm25'] is not None]) if any(h['pm25'] is not None for h in game_hours) else None
                avg_pm10 = sum(h['pm10'] for h in game_hours if h['pm10'] is not None) / len([h for h in game_hours if h['pm10'] is not None]) if any(h['pm10'] is not None for h in game_hours) else None
                
                try:
                    # Store as US AQI (different from PM2.5!)
                    cursor.execute('''
                        INSERT INTO AirQuality 
                        (game_date, location, pollutant_type, pollutant_value, unit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (date, city, 'US_AQI', avg_aqi, 'AQI'))
                    
                    stored_count += 1
                    
                    # Fixed print statement
                    pm25_str = f"{avg_pm25:.1f}" if avg_pm25 is not None else "N/A"
                    print(f"✓ AQI: {avg_aqi:.1f}, PM2.5: {pm25_str}")
                    
                except sqlite3.IntegrityError:
                    print(f"✗ Duplicate")
                    failed_count += 1
            else:
                print(f"✗ No valid data")
                failed_count += 1
        else:
            print(f"✗ No data")
            failed_count += 1
        
        time.sleep(0.3)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM AirQuality")
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
    store_air_quality_data()