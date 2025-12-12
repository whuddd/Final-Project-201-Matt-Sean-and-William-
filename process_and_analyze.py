"""process_and_analyze.py

Load tables from `football_weather.db`, build a joined dataset, compute
aggregations, and export CLEAN, READABLE CSV outputs to `outputs/`.
"""
import argparse
import pandas as pd
import numpy as np
from utils import connect_db, ensure_outputs_dir

def load_data_with_sql_join(conn):
    """
    Load data using a massive SQL join. 
    Note: We select specific columns to keep the dataframe clean from the start.
    """
    query = """
    SELECT 
        g.game_date,
        loc.city_name as stadium_city,
        t_home.team_name AS home_team_name,
        g.home_score,
        g.away_score,
        t_away.team_name AS away_team_name,
        (g.home_score + g.away_score) AS total_points,
        w.temperature,
        w.wind_speed,
        w.precipitation,
        m.moon_illumination,
        m.moon_phase
    FROM Games g
    JOIN Locations loc ON g.location_id = loc.location_id
    JOIN Teams t_home ON g.home_team_id = t_home.team_id
    JOIN Teams t_away ON g.away_team_id = t_away.team_id
    LEFT JOIN Weather w ON g.game_date = w.game_date AND g.location_id = w.location_id
    LEFT JOIN Moon_Data m ON g.game_date = m.game_date AND g.location_id = m.location_id
    ORDER BY g.game_date DESC
    """
    return pd.read_sql_query(query, conn)

def compute_points_by_temperature_bins(joined: pd.DataFrame):
    df = joined.copy()
    temp_col = 'temperature'
    if temp_col not in df.columns:
        df[temp_col] = np.nan

    bins = [-1e9, 39.9, 59.9, 79.9, 1e9]
    labels = ['Below 40 F', '40-59 F', '60-79 F', '80+ F'] # More readable labels
    df['temp_bin'] = pd.cut(df[temp_col].astype(float), bins=bins, labels=labels)

    agg = df.groupby('temp_bin', observed=True).agg(
        count=('total_points', 'count'),
        avg_total_points=('total_points', 'mean'),
        min_score=('total_points', 'min'),
        max_score=('total_points', 'max')
    ).reset_index()

    return agg

def compute_points_by_wind_precip(joined: pd.DataFrame):
    df = joined.copy()
    wind_col = 'wind_speed'
    
    bins = [-1e9, 5.0, 15.0, 1e9]
    labels = ['Low Wind (0-5 mph)', 'Medium Wind (6-15 mph)', 'High Wind (16+ mph)']
    df['wind_bin'] = pd.cut(df[wind_col].astype(float), bins=bins, labels=labels)
    
    # Convert boolean to text immediately for clarity
    df['Condition'] = df.get('precipitation', 0).fillna(0).apply(lambda x: 'Rainy' if x > 0 else 'Dry')

    agg = df.groupby(['wind_bin', 'Condition'], observed=True).agg(
        count=('total_points', 'count'),
        avg_total_points=('total_points', 'mean'),
    ).reset_index()

    return agg

def compute_correlation_matrix(joined: pd.DataFrame):
    df = joined.copy()
    cols = []
    target_cols = ['temperature', 'wind_speed', 'precipitation', 'moon_illumination', 'total_points']
    for c in target_cols:
        if c in df.columns:
            cols.append(c)

    corr = df[cols].apply(pd.to_numeric, errors='coerce').corr(method='pearson')
    return corr

def compute_points_by_moon_illumination(joined: pd.DataFrame):
    df = joined.copy()
    col = 'moon_illumination'
    if col not in df.columns:
        return pd.DataFrame()

    df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0
    df_valid = df[(df[col].notna()) & (df[col] >= 0.0) & (df[col] <= 1.0) & (df['total_points'].notna())].copy()
    
    bins = [0.0, 0.25, 0.5, 0.75, 1.0]
    labels = ['New Moon (0-25%)', 'Crescent (25-50%)', 'Gibbous (50-75%)', 'Full Moon (75-100%)']
    df_valid['moon_bin'] = pd.cut(df_valid[col].astype(float), bins=bins, labels=labels, include_lowest=True)

    agg = df_valid.groupby('moon_bin', observed=True).agg(
        count=('total_points', 'count'),
        avg_total_points=('total_points', 'mean')
    ).reset_index()

    return agg

def compute_win_pct_by_stadium_rain(joined: pd.DataFrame):
    df = joined.copy()
    df['rainy'] = df.get('precipitation', 0).fillna(0) > 0
    df['home_win'] = df['home_score'] > df['away_score']
    
    agg = df.groupby(['stadium_city', 'rainy']).agg(
        num_games=('home_score', 'count'),
        num_wins=('home_win', 'sum')
    ).reset_index()
    
    agg['win_pct'] = agg['num_wins'] / agg['num_games']
    return agg

# --- THE CLEANING FUNCTION ---
def export_clean_csvs(joined, by_temp, by_wind, corr, by_moon, by_rain):
    ensure_outputs_dir()
    
    # 1. Master Dataset: Sort by Date, round numbers, rename columns
    joined_clean = joined.copy()
    joined_clean = joined_clean.round({
        'temperature': 1, 'wind_speed': 1, 'precipitation': 2, 'moon_illumination': 1
    })
    joined_clean = joined_clean.rename(columns={
        'game_date': 'Date',
        'stadium_city': 'Stadium City',
        'home_team_name': 'Home Team',
        'home_score': 'Home Pts',
        'away_score': 'Away Pts',
        'away_team_name': 'Away Team',
        'total_points': 'Total Pts',
        'temperature': 'Temp (F)',
        'wind_speed': 'Wind (mph)',
        'precipitation': 'Precip (in)',
        'moon_illumination': 'Moon %',
        'moon_phase': 'Moon Phase'
    })
    # Reorder for logic: Date -> Location -> Matchup -> Scores -> Weather
    cols_order = ['Date', 'Stadium City', 'Home Team', 'Home Pts', 'Away Pts', 'Away Team', 
                  'Total Pts', 'Temp (F)', 'Wind (mph)', 'Precip (in)', 'Moon %', 'Moon Phase']
    # Only keep columns that exist (in case moon_phase is missing)
    cols_final = [c for c in cols_order if c in joined_clean.columns]
    
    joined_clean[cols_final].to_csv('outputs/joined_dataset.csv', index=False)

    # 2. Temperature Analysis
    if not by_temp.empty:
        temp_clean = by_temp.copy()
        temp_clean.columns = ['Temperature Range', 'Games Played', 'Avg Total Score', 'Lowest Score', 'Highest Score']
        temp_clean = temp_clean.round(1)
        temp_clean.to_csv('outputs/points_by_temp.csv', index=False)

    # 3. Wind Analysis
    if not by_wind.empty:
        wind_clean = by_wind.copy()
        wind_clean.columns = ['Wind Category', 'Weather Condition', 'Games Played', 'Avg Total Score']
        wind_clean = wind_clean.round(1)
        wind_clean.to_csv('outputs/points_by_wind_precip.csv', index=False)

    # 4. Correlation Matrix (Rename index/cols for humans)
    if not corr.empty:
        corr_clean = corr.round(2)
        name_map = {
            'temperature': 'Temp (F)', 'wind_speed': 'Wind (mph)', 'precipitation': 'Precip (in)',
            'moon_illumination': 'Moon Illum %', 'total_points': 'Total Points Scored'
        }
        corr_clean = corr_clean.rename(index=name_map, columns=name_map)
        corr_clean.to_csv('outputs/correlation_matrix.csv')

    # 5. Moon Analysis
    if not by_moon.empty:
        moon_clean = by_moon.copy()
        moon_clean.columns = ['Moon Phase Category', 'Games Played', 'Avg Total Score']
        moon_clean = moon_clean.round(1)
        moon_clean.to_csv('outputs/points_by_moon_illumination.csv', index=False)

    # 6. Win % by Rain
    if not by_rain.empty:
        rain_clean = by_rain.copy()
        rain_clean['rainy'] = rain_clean['rainy'].map({True: 'Rainy', False: 'Dry'})
        rain_clean['win_pct'] = (rain_clean['win_pct'] * 100).round(1)
        rain_clean.columns = ['Stadium', 'Condition', 'Total Games', 'Home Wins', 'Home Win %']
        rain_clean.to_csv('outputs/win_pct_by_stadium_rain.csv', index=False)

    print("\n✅ CLEAN CSVs saved to outputs/")

def main(save_csv=False):
    conn = connect_db()
    print("Loading data...")
    joined = load_data_with_sql_join(conn)
    
    if joined.empty:
        print("Error: No data found.")
        return

    print(f"Loaded {len(joined)} games.")

    # Compute stats
    by_temp = compute_points_by_temperature_bins(joined)
    by_wind = compute_points_by_wind_precip(joined)
    corr = compute_correlation_matrix(joined)
    by_moon = compute_points_by_moon_illumination(joined)
    by_rain = compute_win_pct_by_stadium_rain(joined)

    # Export
    export_clean_csvs(joined, by_temp, by_wind, corr, by_moon, by_rain)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-csv', action='store_true', help='Save CSV outputs to outputs/')
    args = parser.parse_args()
    main(save_csv=args.save_csv)
