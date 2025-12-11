"""visualize.py

Produce four Matplotlib/Seaborn visualizations from outputs/joined_dataset.csv
and aggregated CSVs created by `process_and_analyze.py`.

Run after running processing script with `--save-csv`:
    python visualize.py

Outputs saved to `outputs/figures/`.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='whitegrid')


def ensure_fig_dir():
    os.makedirs('outputs/figures', exist_ok=True)


def plot_temp_bins():
    df = pd.read_csv('outputs/points_by_temp.csv')
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='temp_bin', y='avg_total_points', palette='viridis')
    plt.ylabel('Average Total Points')
    plt.xlabel('Temperature Bin (°F)')
    plt.title('Average Total Points by Temperature Bin')
    plt.tight_layout()
    plt.savefig('outputs/figures/fig1_temperature.png')
    plt.close()


def plot_wind_precip_box(joined_csv='outputs/joined_dataset.csv'):
    df = pd.read_csv(joined_csv)
    # create wind_bin and precip_flag like processing
    if 'wind_speed' not in df.columns:
        df['wind_speed'] = pd.NA
    df['wind_bin'] = pd.cut(df['wind_speed'].astype(float), bins=[-1e9,5,15,1e9], labels=['0-5','6-15','16+'])
    df['precip_flag'] = df.get('precipitation', 0).fillna(0) > 0

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='wind_bin', y='total_points', hue='precip_flag', palette='Set2')
    plt.ylabel('Total Points')
    plt.xlabel('Wind Speed Bin (mph)')
    plt.title('Total Points by Wind Bin and Precipitation')
    plt.legend(title='Precipitation')
    plt.tight_layout()
    plt.savefig('outputs/figures/fig2_wind_precip.png')
    plt.close()


def plot_correlation():
    corr = pd.read_csv('outputs/correlation_matrix.csv', index_col=0)
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.savefig('outputs/figures/fig3_correlation_heatmap.png')
    plt.close()


def plot_moon_illumination(joined_csv='outputs/joined_dataset.csv'):
    df = pd.read_csv(joined_csv)
    if 'moon_illumination' not in df.columns:
        print('No moon_illumination column found; skipping moon plot')
        return

    # Normalize moon_illumination to 0-1 range (data is in 0-100)
    df['moon_illumination'] = pd.to_numeric(df['moon_illumination'], errors='coerce') / 100.0
    
    plt.figure(figsize=(8, 6))
    sns.regplot(data=df, x='moon_illumination', y='total_points', scatter_kws={'s': 20}, line_kws={'color': 'red'})
    plt.xlabel('Moon Illumination (0-1)')
    plt.ylabel('Total Points')
    plt.title('Moon Illumination vs Total Points')
    plt.tight_layout()
    plt.savefig('outputs/figures/fig4_moon_illumination.png')
    plt.close()


def plot_win_pct_by_stadium_rain():
    df = pd.read_csv('outputs/win_pct_by_stadium_rain.csv')
    
    if df.empty:
        print('No win percentage by stadium/rain data; skipping plot')
        return
    
    # Convert win_pct to percentage (0-100 scale)
    df['win_pct_pct'] = df['win_pct'] * 100
    
    # Sort by stadium_city alphabetically for readability
    df = df.sort_values('stadium_city')
    
    # Create custom color palette: blue for dry, red for rainy
    palette = {False: '#2E86AB', True: '#E63946'}
    
    plt.figure(figsize=(14, 6))
    ax = sns.barplot(data=df, x='stadium_city', y='win_pct_pct', hue='rainy', palette=palette)
    plt.xlabel('Stadium City', fontsize=12)
    plt.ylabel('Home Win %', fontsize=12)
    plt.title('Home Win % in Rain vs Dry Games by Stadium', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    # Update legend with proper colors
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, ['No (Dry)', 'Yes (Rainy)'], title='Rainy', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('outputs/figures/fig5_win_pct_rain_by_stadium.png', dpi=100)
    plt.close()


def main():
    ensure_fig_dir()
    plot_temp_bins()
    plot_wind_precip_box()
    plot_correlation()
    plot_moon_illumination()
    plot_win_pct_by_stadium_rain()
    print('Figures saved to outputs/figures/')


if __name__ == '__main__':
    main()
