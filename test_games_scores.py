# football_data.py
# William - College Football Data Collection
# Run this 4+ times to collect 100+ games

import sqlite3
import requests
from config import COLLEGE_FOOTBALL_KEY
import time

# Map EXACT stadium names to our weather cities
STADIUM_TO_CITY = {
    'Michigan Stadium': 'Ann Arbor',
    'Ohio Stadium': 'Columbus',
    'Beaver Stadium': 'State College',
    'Camp Randall Stadium': 'Madison',
    'Kinnick Stadium': 'Iowa City',
    'Autzen Stadium': 'Eugene',
    'DKR-Texas Memorial Stadium': 'Austin',
    'Bryant-Denny Stadium': 'Tuscaloosa',
    'Sanford Stadium': 'Athens',
    'Tiger Stadium (LA)': 'Baton Rouge',
}

def get_or_create_team(cursor, team_name, conference="Unknown", city="Unknown"):
    """Get team_id or create new team (avoids duplicate team names)"""
    cursor.execute("SELECT team_id FROM Teams WHERE team_name = ?", (team_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute(
            "INSERT INTO Teams (team_name, conference, stadium_city) VALUES (?, ?, ?)",
            (team_name, conference, city)
        )
        return cursor.lastrowid

def get_games_from_api(year=2023, week=1):
    """Get games from CollegeFootballData API"""
    url = "https://api.collegefootballdata.com/games"
    
    headers = {'Authorization': f'Bearer {COLLEGE_FOOTBALL_KEY}'}
    params = {'year': year, 'week': week, 'seasonType': 'regular'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error {response.status_code}")
            return []
    except Exception as e:
        print(f"  Exception: {e}")
        return []

def get_city_from_venue(venue_name):
    """Map venue/stadium name to our weather city"""
    if not venue_name:
        return None
    
    # Check if exact stadium name matches
    if venue_name in STADIUM_TO_CITY:
        return STADIUM_TO_CITY[venue_name]
    
    # Also check partial matches
    for stadium, city in STADIUM_TO_CITY.items():
        if stadium in venue_name:
            return city
    
    return None

def show_database_stats():
    """Show current database statistics"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Games")
    total_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Teams")
    total_teams = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT stadium_city, COUNT(*) 
        FROM Games 
        GROUP BY stadium_city 
        ORDER BY COUNT(*) DESC
    """)
    by_city = cursor.fetchall()
    
    cursor.execute("""
        SELECT g.game_date, t1.team_name, g.home_score, g.away_score, t2.team_name, g.stadium_city
        FROM Games g
        JOIN Teams t1 ON g.home_team_id = t1.team_id
        JOIN Teams t2 ON g.away_team_id = t2.team_id
        ORDER BY g.game_date DESC
        LIMIT 5
    """)
    sample_games = cursor.fetchall()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total games: {total_games}")
    print(f"Total teams: {total_teams}")
    
    if by_city:
        print("\nGames by city:")
        for city, count in by_city:
            print(f"  {city}: {count}")
    
    if sample_games:
        print("\nMost recent games:")
        for date, home, h_score, a_score, away, city in sample_games:
            print(f"  {date} ({city}): {home} {h_score}-{a_score} {away}")
    
    conn.close()
    return total_games

def store_football_data():
    """Store up to 25 games per run from 2023 season"""
    conn = sqlite3.connect('football_weather.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Games")
    actual_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT game_id FROM Games")
    existing_game_ids = set(row[0] for row in cursor.fetchall())
    
    print(f"\n{'='*60}")
    print(f"FOOTBALL DATA COLLECTION - 2023 SEASON")
    print(f"{'='*60}")
    print(f"Current games: {actual_count}")
    print(f"Target stadiums: {len(STADIUM_TO_CITY)}")
    print(f"{'='*60}\n")
    
    stored_count = 0
    skipped_count = 0
    no_score_count = 0
    wrong_venue_count = 0
    
    for week in range(1, 15):
        if stored_count >= 25:
            print(f"\n✓ Reached 25-item limit")
            break
        
        print(f"Week {week}...", end=" ")
        games = get_games_from_api(2023, week)
        
        if not games:
            print("No games")
            continue
        
        # Count valid games
        valid_games = 0
        for g in games:
            venue_name = g.get('venue', '')
            city = get_city_from_venue(venue_name)
            # FIXED: Check top-level homePoints
            if city and g.get('homePoints') is not None:
                valid_games += 1
        
        print(f"{len(games)} total, {valid_games} valid")
        
        for game in games:
            if stored_count >= 25:
                break
            
            game_id = game.get('id')
            if game_id in existing_game_ids:
                skipped_count += 1
                continue
            
            # FIXED: Get venue as string directly
            venue_name = game.get('venue', '')
            stadium_city = get_city_from_venue(venue_name)
            
            if not stadium_city:
                wrong_venue_count += 1
                continue
            
            # FIXED: Get scores from top level
            home_score = game.get('homePoints')
            away_score = game.get('awayPoints')
            
            if home_score is None or away_score is None:
                no_score_count += 1
                continue
            
            # FIXED: Get team info from top level
            home_team = game.get('homeTeam', 'Unknown')
            away_team = game.get('awayTeam', 'Unknown')
            home_conference = game.get('homeConference', 'Unknown')
            away_conference = game.get('awayConference', 'Unknown')
            
            # Extract game date
            game_date = game.get('startDate', '')[:10]
            
            # Get or create team IDs
            home_team_id = get_or_create_team(cursor, home_team, home_conference, stadium_city)
            away_team_id = get_or_create_team(cursor, away_team, away_conference, stadium_city)
            
            # Insert game
            try:
                cursor.execute('''
                    INSERT INTO Games 
                    (game_id, game_date, home_team_id, away_team_id, 
                     home_score, away_score, stadium_city)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (game_id, game_date, home_team_id, away_team_id,
                      home_score, away_score, stadium_city))
                
                stored_count += 1
                total = home_score + away_score
                print(f"  [{stored_count}] {game_date} ({stadium_city}): {home_team} {home_score}-{away_score} {away_team}")
                
            except sqlite3.IntegrityError:
                skipped_count += 1
        
        time.sleep(0.3)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM Games")
    final_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"COLLECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Added: {stored_count}")
    print(f"Skipped (duplicate): {skipped_count}")
    print(f"Skipped (wrong venue): {wrong_venue_count}")
    print(f"Skipped (no score): {no_score_count}")
    print(f"Total games now: {final_count}")
    
    if final_count < 100:
        runs_needed = ((100 - final_count) // 25) + 1
        print(f"Need {runs_needed} more runs to reach 100")
    else:
        print("✅ 100+ games collected!")
    
    print(f"{'='*60}\n")
    show_database_stats()

if __name__ == '__main__':
    store_football_data()