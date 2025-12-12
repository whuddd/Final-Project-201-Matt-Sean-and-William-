import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def ensure_figures_dir():
    """Creates a 'figures' folder if it doesn't exist."""
    if not os.path.exists('figures'):
        os.makedirs('figures')

# ==========================================
# 1. TEMPERATURE CHART (Fixed Text Color)
# ==========================================
def plot_temp_impact():
    try:
        df = pd.read_csv('outputs/points_by_temp.csv')
    except FileNotFoundError:
        print("❌ Missing points_by_temp.csv")
        return

    # Filter empty bins
    df = df[df['count'] > 0].copy().reset_index(drop=True)

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        data=df, 
        x='temp_bin', 
        y='avg_total_points', 
        hue='temp_bin', 
        palette='RdBu_r', 
        edgecolor='black'
    )

    for i, row in df.iterrows():
        height = row['avg_total_points']
        count = int(row['count'])
        
        # --- COLOR FIX ---
        # If it's the middle bar (index 1), use BLACK text. 
        # For the dark blue/red outer bars, use WHITE text.
        text_color = 'black' if i == 1 else 'white'
        
        ax.text(i, height + 1, f'{height:.1f} pts', ha='center', fontweight='bold', color='black') # Score is always black
        ax.text(i, height - 4, f'(n={count})', ha='center', color=text_color, fontweight='bold') # Count changes color

    plt.title('Impact of Temperature on Total Scoring', fontsize=14)
    plt.xlabel('Temperature (°F)', fontsize=12)
    plt.ylabel('Average Total Points', fontsize=12)
    plt.ylim(0, max(df['avg_total_points']) * 1.2)
    
    ensure_figures_dir()
    plt.savefig('figures/1_temperature_impact.png', dpi=300, bbox_inches='tight')
    print("✅ Saved chart: figures/1_temperature_impact.png")
    plt.close()

# ==========================================
# 2. WIND SPEED CHART (Bar Chart)
# ==========================================
def plot_wind_impact():
    try:
        df = pd.read_csv('outputs/points_by_wind_precip.csv')
    except FileNotFoundError:
        print("❌ Missing points_by_wind_precip.csv")
        return

    df_wind = df.groupby('wind_bin', observed=True).agg({
        'avg_total_points': 'mean', 
        'count': 'sum'
    }).reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=df_wind, 
        x='wind_bin', 
        y='avg_total_points', 
        hue='wind_bin', 
        palette='viridis', 
        edgecolor='black'
    )

    for i, row in df_wind.iterrows():
        height = row['avg_total_points']
        count = int(row['count'])
        if count > 0:
            ax.text(i, height + 0.5, f'{height:.1f}', ha='center', fontweight='bold')
            ax.text(i, height - 3, f'n={count}', ha='center', color='white', fontsize=9)

    plt.title('Does Wind Speed Affect Scoring?', fontsize=14)
    plt.xlabel('Wind Speed (mph)', fontsize=12)
    plt.ylabel('Average Total Points', fontsize=12)
    
    ensure_figures_dir()
    plt.savefig('figures/2_wind_impact.png', dpi=300, bbox_inches='tight')
    print("✅ Saved chart: figures/2_wind_impact.png")
    plt.close()

# ==========================================
# 3. RAIN: SCORING VARIANCE (Box Plot)
# ==========================================
def plot_rain_scoring():
    try:
        df = pd.read_csv('outputs/joined_dataset.csv')
    except FileNotFoundError:
        print("❌ Missing joined_dataset.csv")
        return

    df['Condition'] = df['precipitation'].apply(lambda x: 'Rain' if x > 0 else 'Dry')

    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='Condition', y='total_points', palette=['skyblue', 'gray'])
    sns.stripplot(data=df, x='Condition', y='total_points', color='black', alpha=0.3)

    plt.title('Scoring Distribution: Rain vs. Dry Games', fontsize=14)
    plt.ylabel('Total Points Scored', fontsize=12)
    
    ensure_figures_dir()
    plt.savefig('figures/3_rain_scoring_box.png', dpi=300, bbox_inches='tight')
    print("✅ Saved chart: figures/3_rain_scoring_box.png")
    plt.close()

# ==========================================
# 4. RAIN: HOME WIN % (Restored Bar Chart)
# ==========================================
def plot_rain_win_pct():
    try:
        df = pd.read_csv('outputs/win_pct_by_stadium_rain.csv')
    except FileNotFoundError:
        print("❌ Missing win_pct_by_stadium_rain.csv")
        return

    # Convert 0.8 to 80.0 for better readability
    df['win_pct'] = df['win_pct'] * 100
    
    # Create Labels for the Legend
    df['Weather'] = df['rainy'].apply(lambda x: 'Yes (Rainy)' if x else 'No (Dry)')

    plt.figure(figsize=(14, 7))
    sns.barplot(
        data=df, 
        x='stadium_city', 
        y='win_pct', 
        hue='Weather', 
        palette={'No (Dry)': '#4c7d9e', 'Yes (Rainy)': '#c44e52'}
    )

    plt.title('Home Win % in Rain vs Dry Games by Stadium', fontsize=16)
    plt.ylabel('Home Win %', fontsize=12)
    plt.xlabel('Stadium City', fontsize=12)
    plt.xticks(rotation=45, ha='right') # Rotate labels so they don't overlap
    plt.legend(title='Rainy Condition')
    plt.tight_layout()
    
    ensure_figures_dir()
    plt.savefig('figures/4_rain_win_pct.png', dpi=300, bbox_inches='tight')
    print("✅ Saved chart: figures/4_rain_win_pct.png")
    plt.close()

# ==========================================
# 5. CORRELATION HEATMAP
# ==========================================
def plot_correlation():
    try:
        df = pd.read_csv('outputs/correlation_matrix.csv', index_col=0)
    except FileNotFoundError:
        print("❌ Missing correlation_matrix.csv")
        return

    plt.figure(figsize=(10, 8))
    sns.heatmap(df, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)

    plt.title('Correlation Matrix (Variables vs. Scoring)', fontsize=14)
    plt.tight_layout()
    
    ensure_figures_dir()
    plt.savefig('figures/5_correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("✅ Saved chart: figures/5_correlation_matrix.png")
    plt.close()

if __name__ == "__main__":
    ensure_figures_dir()
    plot_temp_impact()
    plot_wind_impact()
    plot_rain_scoring()
    plot_rain_win_pct()
    plot_correlation()
    print("\n🎉 All 5 visualizations saved to the 'figures/' folder!")