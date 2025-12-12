import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def ensure_figures_dir():
    if not os.path.exists('figures'):
        os.makedirs('figures')

# 1. TEMPERATURE CHART
def plot_temp_impact():
    try:
        df = pd.read_csv('outputs/points_by_temp.csv')
    except FileNotFoundError:
        print("❌ Missing points_by_temp.csv")
        return

    # Filter empty bins. New column names:
    df = df[df['Games Played'] > 0].copy().reset_index(drop=True)

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        data=df, 
        x='Temperature Range',      # Updated name
        y='Avg Total Points',       # Updated name
        hue='Temperature Range', 
        palette='RdBu_r', 
        edgecolor='black'
    )

    for i, row in df.iterrows():
        height = row['Avg Total Points']
        count = int(row['Games Played'])
        text_color = 'black' if i == 1 else 'white'
        ax.text(i, height + 1, f'{height:.1f} pts', ha='center', fontweight='bold', color='black')
        ax.text(i, height - 4, f'(n={count})', ha='center', color=text_color, fontweight='bold')

    plt.title('Impact of Temperature on Total Scoring', fontsize=14)
    plt.xlabel('Temperature (°F)', fontsize=12)
    plt.ylabel('Average Total Points', fontsize=12)
    plt.ylim(0, max(df['Avg Total Points']) * 1.2)
    
    ensure_figures_dir()
    plt.savefig('figures/1_temperature_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved chart 1")

# 2. WIND SPEED CHART
def plot_wind_impact():
    try:
        df = pd.read_csv('outputs/points_by_wind_precip.csv')
    except FileNotFoundError:
        return

    # Use new column names
    df_wind = df.groupby('Wind Speed').agg({
        'Avg Total Points': 'mean', 
        'Games Played': 'sum'
    }).reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=df_wind, 
        x='Wind Speed', 
        y='Avg Total Points', 
        hue='Wind Speed', 
        palette='viridis', 
        edgecolor='black'
    )

    for i, row in df_wind.iterrows():
        height = row['Avg Total Points']
        count = int(row['Games Played'])
        if count > 0:
            ax.text(i, height + 0.5, f'{height:.1f}', ha='center', fontweight='bold')
            ax.text(i, height - 3, f'n={count}', ha='center', color='white', fontsize=9)

    plt.title('Does Wind Speed Affect Scoring?', fontsize=14)
    plt.xlabel('Wind Speed (mph)', fontsize=12)
    plt.ylabel('Average Total Points', fontsize=12)
    
    ensure_figures_dir()
    plt.savefig('figures/2_wind_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved chart 2")

# 3. RAIN SCORING (Box Plot)
def plot_rain_scoring():
    try:
        df = pd.read_csv('outputs/joined_dataset.csv')
    except FileNotFoundError:
        return

    # Create condition column from Precip column
    df['Condition'] = df['Precip (in)'].apply(lambda x: 'Rain' if x > 0 else 'Dry')

    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='Condition', y='Total Points', palette=['skyblue', 'gray'])
    sns.stripplot(data=df, x='Condition', y='Total Points', color='black', alpha=0.3)

    plt.title('Scoring Distribution: Rain vs. Dry Games', fontsize=14)
    plt.ylabel('Total Points Scored', fontsize=12)
    
    ensure_figures_dir()
    plt.savefig('figures/3_rain_scoring_box.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved chart 3")

# 4. RAIN WIN PCT
def plot_rain_win_pct():
    try:
        df = pd.read_csv('outputs/win_pct_by_stadium_rain.csv')
    except FileNotFoundError:
        return

    plt.figure(figsize=(14, 7))
    sns.barplot(
        data=df, 
        x='Stadium',      # New name
        y='Home Win %',   # New name
        hue='Weather',    # New name
        palette={'Dry': '#4c7d9e', 'Rainy': '#c44e52'}
    )

    plt.title('Home Win % in Rain vs Dry Games by Stadium', fontsize=16)
    plt.ylabel('Home Win %', fontsize=12)
    plt.xlabel('Stadium City', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Condition')
    plt.tight_layout()
    
    ensure_figures_dir()
    plt.savefig('figures/4_rain_win_pct.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved chart 4")

# 5. CORRELATION
def plot_correlation():
    try:
        df = pd.read_csv('outputs/correlation_matrix.csv', index_col=0)
    except FileNotFoundError:
        return

    plt.figure(figsize=(10, 8))
    sns.heatmap(df, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)

    plt.title('Correlation Matrix', fontsize=14)
    plt.tight_layout()
    
    ensure_figures_dir()
    plt.savefig('figures/5_correlation_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved chart 5")

if __name__ == "__main__":
    ensure_figures_dir()
    plot_temp_impact()
    plot_wind_impact()
    plot_rain_scoring()
    plot_rain_win_pct()
    plot_correlation()
    print("\n🎉 All 5 updated visualizations saved!")