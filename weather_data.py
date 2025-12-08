import sqlite3
import requests
from datetime import datetime, timedelta
import time

# Stadium coordinates (major college football cities)
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
            print(f"  Error {response.status_code}")
            return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def store_weather_data():
    """
    Store up to 25 weather records per run
    """
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    # Check current count
    cursor.execute("SELECT COUNT(*) FROM Weather")
    current_count = cursor.fetchone()[0]
    print(f"Current weather records in database: {current_count}")
    
    # Check existing records
    cursor.execute("SELECT game_date, location FROM Weather")
    existing = set(cursor.fetchall())
    print(f"Already have {len(existing)} unique date-location combinations")
    
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
    
    print(f"Found {len(all_combinations)} new date-location combinations to collect")
    
    if len(all_combinations) == 0:
        print("⚠️  No new data to collect! All combinations already in database.")
        conn.close()
        return
    
    stored_count = 0
    
    # Collect data from the list of new combinations
    for date, city, coords in all_combinations:
        if stored_count >= 25:
            break
        
        print(f"Fetching historical weather for {city} on {date}...")
        weather = get_weather_from_api(coords['lat'], coords['lon'], date)
        
        if weather:
            cursor.execute('''
                INSERT INTO Weather 
                (game_date, location, temperature, wind_speed, 
                 humidity, precipitation, weather_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, city, weather['temperature'], weather['wind_speed'],
                  weather['humidity'], weather['precipitation'], 
                  weather['weather_code']))
            
            stored_count += 1
            print(f"  ✓ Stored: {city} - Temp: {weather['temperature']:.1f}°F, Wind: {weather['wind_speed']:.1f} mph")
        
        # Small delay to be nice to the API
        time.sleep(0.5)
    
    conn.commit()
    conn.close()
    
    total = current_count + stored_count
    remaining = len(all_combinations) - stored_count
    
    print(f"\n{'='*60}")
    print(f"✅ Stored {stored_count} new weather records")
    print(f"📊 Total weather records: {total}")
    print(f"🔄 Remaining combinations: {remaining}")
    print(f"🔄 Need to run {max(0, remaining // 25 + (1 if remaining % 25 else 0))} more times to collect all available data")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    store_weather_data()
