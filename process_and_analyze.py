"""process_and_analyze.py

Load tables from `football_weather.db`, build a joined dataset, compute
aggregations (points by temperature/wind/precipitation bins), compute a
correlation matrix, and export CSV outputs to `outputs/`.

Run:
    python process_and_analyze.py --save-csv

"""
import argparse
import pandas as pd
import numpy as np
from utils import connect_db, normalize_location, ensure_outputs_dir



def load_data_with_sql_join(conn):
    query = """
    SELECT 
        g.game_date,
        loc.city_name as stadium_city,  -- Get text from Locations table
        g.home_score,
        g.away_score,
        (g.home_score + g.away_score) AS total_points,
        t_home.team_name AS home_team_name,
        t_away.team_name AS away_team_name,
        w.temperature,
        w.wind_speed,
        w.precipitation,
        m.moon_illumination
    FROM Games g
    -- JOIN Locations to get the city name
    JOIN Locations loc ON g.location_id = loc.location_id
    JOIN Teams t_home ON g.home_team_id = t_home.team_id
    JOIN Teams t_away ON g.away_team_id = t_away.team_id
    -- Link Weather using Date + Location ID
    LEFT JOIN Weather w ON g.game_date = w.game_date AND g.location_id = w.location_id
    -- Link Moon Data using Date + Location ID
    LEFT JOIN Moon_Data m ON g.game_date = m.game_date AND g.location_id = m.location_id
    """
    return pd.read_sql_query(query, conn)



def compute_points_by_temperature_bins(joined: pd.DataFrame):
    """Bin temperatures and compute average points.

    Fixed bins: <40, 40-59, 60-79, 80+
    """
    df = joined.copy()
    # Ensure temperature column exists
    temp_col = 'temperature'
    if temp_col not in df.columns:
        df[temp_col] = np.nan

    bins = [-1e9, 39.9, 59.9, 79.9, 1e9]
    labels = ['<40', '40-59', '60-79', '80+']
    df['temp_bin'] = pd.cut(df[temp_col].astype(float), bins=bins, labels=labels)

    agg = df.groupby('temp_bin').agg(
        count=('total_points', 'count'),
        avg_total_points=('total_points', 'mean'),
        avg_home_points=('home_score', 'mean'),
        avg_away_points=('away_score', 'mean'),
        std_total_points=('total_points', 'std')
    ).reset_index()

    return agg


def compute_points_by_wind_precip(joined: pd.DataFrame):
    df = joined.copy()
    wind_col = 'wind_speed'
    if wind_col not in df.columns:
        df[wind_col] = np.nan

    # Wind bins: 0-5, 6-15, 16+
    bins = [-1e9, 5.0, 15.0, 1e9]
    labels = ['0-5', '6-15', '16+']
    df['wind_bin'] = pd.cut(df[wind_col].astype(float), bins=bins, labels=labels)
    df['precip_flag'] = df.get('precipitation', 0).fillna(0) > 0

    agg = df.groupby(['wind_bin', 'precip_flag']).agg(
        count=('total_points', 'count'),
        avg_total_points=('total_points', 'mean'),
    ).reset_index()

    return agg


def compute_correlation_matrix(joined: pd.DataFrame):
    df = joined.copy()
    # Select numeric columns of interest
    cols = []
    for c in ['temperature', 'wind_speed', 'humidity', 'precipitation', 'us_aqi', 'moon_illumination', 'total_points', 'attendance']:
        if c in df.columns:
            cols.append(c)

    corr = df[cols].apply(pd.to_numeric, errors='coerce').corr(method='pearson')
    return corr


def compute_points_by_moon_illumination(joined: pd.DataFrame):
    df = joined.copy()
    col = 'moon_illumination'
    if col not in df.columns:
        return pd.DataFrame(columns=['moon_bin', 'count', 'avg_total_points'])

    # Normalize moon_illumination to 0-1 range (data is in 0-100 range)
    df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0
    
    # Filter to valid rows: moon_illumination is not null and between 0-1, total_points is not null
    df_valid = df[(df[col].notna()) & (df[col] >= 0.0) & (df[col] <= 1.0) & (df['total_points'].notna())].copy()
    
    if len(df_valid) == 0:
        # Return empty frame with correct schema
        return pd.DataFrame(columns=['moon_bin', 'count', 'avg_total_points'])

    bins = [0.0, 0.25, 0.5, 0.75, 1.0]
    labels = ['0-0.25', '0.25-0.5', '0.5-0.75', '0.75-1.0']
    df_valid['moon_bin'] = pd.cut(df_valid[col].astype(float), bins=bins, labels=labels, include_lowest=True)

    agg = df_valid.groupby('moon_bin').agg(
        count=('total_points', 'count'),
        avg_total_points=('total_points', 'mean')
    ).reset_index()

    return agg


def compute_win_pct_by_stadium_rain(joined: pd.DataFrame):
    """Compute home win percentage by stadium and rain condition.
    
    Rainy = precipitation > 0.
    """
    df = joined.copy()
    
    # Ensure necessary columns
    if 'stadium_city' not in df.columns or 'home_score' not in df.columns or 'away_score' not in df.columns:
        return pd.DataFrame(columns=['stadium_city', 'rainy', 'num_games', 'num_wins', 'win_pct'])
    
    # Define rainy games
    df['rainy'] = df.get('precipitation', 0).fillna(0) > 0
    df['home_win'] = df['home_score'] > df['away_score']
    
    # Group by stadium_city and rainy
    agg = df.groupby(['stadium_city', 'rainy']).agg(
        num_games=('home_score', 'count'),
        num_wins=('home_win', 'sum')
    ).reset_index()
    
    # Compute win percentage
    agg['win_pct'] = agg['num_wins'] / agg['num_games']
    
    return agg


def export_csvs(joined, by_temp, by_wind_precip, corr, by_moon, by_rain):
    ensure_outputs_dir()
    joined.to_csv('outputs/joined_dataset.csv', index=False)
    by_temp.to_csv('outputs/points_by_temp.csv', index=False)
    by_wind_precip.to_csv('outputs/points_by_wind_precip.csv', index=False)
    corr.to_csv('outputs/correlation_matrix.csv')
    by_moon.to_csv('outputs/points_by_moon_illumination.csv', index=False)
    by_rain.to_csv('outputs/win_pct_by_stadium_rain.csv', index=False)


def main(save_csv=False):
    conn = connect_db()
    
    # --- OLD CODE DELETED ---
    # tables = load_tables(conn)
    # tables = normalize_tables(tables)
    # joined = build_joined_dataset(tables)
    
    # --- NEW CODE ADDED ---
    print("Loading data with SQL JOIN...")
    joined = load_data_with_sql_join(conn)

    if joined.shape[0] == 0:
        print('ERROR: joined dataset has 0 rows. Verify database content.')
        return

    print(f'Joined rows: {joined.shape[0]}')
    
    # ... The rest of your main function stays exactly the same ...
    by_temp = compute_points_by_temperature_bins(joined)
    # etc...
    by_wind_precip = compute_points_by_wind_precip(joined)
    corr = compute_correlation_matrix(joined)
    by_moon = compute_points_by_moon_illumination(joined)
    by_rain = compute_win_pct_by_stadium_rain(joined)

    print('\nPoints by temperature bins:')
    print(by_temp.head())

    print('\nPoints by wind/precipitation:')
    print(by_wind_precip.head())

    print('\nHome win % by stadium and rain:')
    print(by_rain.head(10))

    print('\nTop correlations (abs > 0.3):')
    if not corr.empty:
        flat = corr.abs().unstack().sort_values(ascending=False).drop_duplicates()
        print(flat[flat > 0.3].head(10))
    else:
        print('No correlation data available')

    export_csvs(joined, by_temp, by_wind_precip, corr, by_moon, by_rain)
    print('\nCSV outputs written to outputs/*.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-csv', action='store_true', help='Save CSV outputs to outputs/')
    args = parser.parse_args()
    main(save_csv=args.save_csv)
