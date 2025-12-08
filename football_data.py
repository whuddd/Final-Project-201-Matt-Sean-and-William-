import sqlite3

def clear_database():
    """Clear all data from tables but keep the structure"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    print("Clearing all tables...")
    
    # Delete all data from each table
    cursor.execute("DELETE FROM Games")
    cursor.execute("DELETE FROM Teams")
    cursor.execute("DELETE FROM AirQuality")
    cursor.execute("DELETE FROM UV_Data")
    
    conn.commit()
    
    # Show counts to verify
    tables = ['Games', 'Teams', 'Weather', 'AirQuality', 'UV_Data']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    conn.close()
    print("\n✅ Database cleared!")

if __name__ == '__main__':
    clear_database()