import requests
import pandas as pd
import sqlite3
from config import OPENUV_KEY

# 1. Use the HISTORY endpoint (Retrieve UV Index History by Date)
# Based on your documentation: GET /api/uvindex/history
# (Note: We try the standard v1 path 'api/v1/uv/history' based on the domain)
url = "https://api.openuv.io/api/v1/uv/history"

# 2. Parameters
# We use 'date' (YYYY-MM-DD) to get the whole day, not 'dt'
params = {
    "lat": 42.2808,       # Ann Arbor Latitude
    "lng": -83.7430,      # Ann Arbor Longitude
    "date": "2024-10-12"  # The specific day of the football game
}

headers = {
    "x-access-token": OPENUV_KEY.strip(),
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # 3. The 'result' is now a LIST of hourly data points, not just one dictionary
        history_list = data.get('result', [])
        
        # 4. Convert the list directly to a DataFrame
        df = pd.DataFrame(history_list)
        
        # 5. Clean up the DataFrame
        # Keep only the columns you need
        if not df.empty:
            # Select relevant columns (uv, uv_time, ozone)
            df = df[['uv_time', 'uv', 'ozone']]
            
            # Convert time to readable format
            df['uv_time'] = pd.to_datetime(df['uv_time'])
            
            # Rename columns
            df = df.rename(columns={'uv_time': 'Date_Time', 'uv': 'UV_Index'})
            
            print("--- Full Day Data Retrieved ---")
            print(df.head(24)) # Show the first 24 rows (hours)

            # 6. Save to SQLite
            conn = sqlite3.connect("weather_data.db")
            df.to_sql('openuv_full_day', conn, if_exists='append', index=False)
            conn.close()
            print("\nSuccess! Saved full day to 'openuv_full_day' table.")
        else:
            print("No data found for this date.")

    # ERROR HANDLING FOR PERMISSIONS
    elif response.status_code == 403:
        print("Error 403: Forbidden.")
        print("Your OpenUV plan might not support the 'History' endpoint.")
        print("Try using the Open-Meteo code provided earlier (it is free/unlimited).")
    
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")