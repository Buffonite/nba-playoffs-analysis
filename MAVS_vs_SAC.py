from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog, playbyplayv2, boxscoretraditionalv2
import pandas as pd
import time
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Get team ID for Kings
team_id_kings = teams.find_teams_by_full_name("Sacramento Kings")[0]['id']
season = '2024-25'

# 2. Get all Kings games and filter SAC vs DAL
games = teamgamelog.TeamGameLog(team_id=team_id_kings, season=season).get_data_frames()[0]
sac_vs_dal = games[games['MATCHUP'].str.contains('DAL')]
game_ids = sac_vs_dal['Game_ID'].tolist()

# 3. Get per-quarter points for each player
all_player_stats = []

for game_id in game_ids:
    pbp = playbyplayv2.PlayByPlayV2(game_id=game_id).get_data_frames()[0]

    points_events = pbp[pbp['EVENTMSGTYPE'].isin([1, 3])]
    points_events['PTS'] = points_events['EVENTMSGTYPE'].apply(lambda x: 2 if x == 1 else 1)
    points_events['PTS'] = points_events.apply(
        lambda row: 3 if row['EVENTMSGTYPE'] == 1 and '3PT' in str(row['HOMEDESCRIPTION']) else row['PTS'], axis=1
    )

    game_stats = points_events.groupby(['PERIOD', 'PLAYER1_NAME'])['PTS'].sum().reset_index()
    game_stats['GAME_ID'] = game_id
    all_player_stats.append(game_stats)
    
    time.sleep(0.6)

df = pd.concat(all_player_stats)

# 4. Get PLUS_MINUS and TEAM from box score
plus_minus_list = []

for game_id in game_ids:
    box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    pm_df = box.get_data_frames()[0][['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PLUS_MINUS']]
    pm_df['GAME_ID'] = game_id
    plus_minus_list.append(pm_df)
    
    time.sleep(0.6)

pm_df = pd.concat(plus_minus_list)

# 5. Merge scoring and plus-minus data
merged = df.merge(pm_df, left_on=['PLAYER1_NAME', 'GAME_ID'], right_on=['PLAYER_NAME', 'GAME_ID'], how='left')

# 6. Calculate avg 4th quarter points
q4 = merged[merged['PERIOD'] == 4]
avg_q4_pts = q4.groupby('PLAYER1_NAME')['PTS'].mean().reset_index()
avg_q4_pts.rename(columns={'PTS': 'avg_4Q_pts'}, inplace=True)

# 7. Full summary
summary = merged.groupby(['PLAYER1_NAME', 'TEAM_ABBREVIATION']).agg(
    total_pts=('PTS', 'sum'),
    avg_pts_per_game=('PTS', 'mean'),
    avg_plus_minus=('PLUS_MINUS', 'mean'),
    games_played=('GAME_ID', 'nunique')
).reset_index()

# 8. Merge 4th quarter points
summary = summary.merge(avg_q4_pts, on='PLAYER1_NAME', how='left')
summary_kings = summary[summary['TEAM_ABBREVIATION'] == 'SAC']
summary_mavs = summary[summary['TEAM_ABBREVIATION'] == 'DAL']
print(summary_kings)
print(summary_mavs)
# 9. Plot: 4Q points vs Plus/Minus
plt.figure(figsize=(10, 6))
sns.scatterplot(data=summary, x='avg_4Q_pts', y='avg_plus_minus', hue='TEAM_ABBREVIATION', s=100)

# Add player labels
for _, row in summary.iterrows():
    plt.text(row['avg_4Q_pts'] + 0.1, row['avg_plus_minus'], row['PLAYER1_NAME'], fontsize=9)

plt.title('SAC vs DAL — 4th Quarter Points vs Plus/Minus')
plt.xlabel('Avg 4Q Points')
plt.ylabel('Avg Plus/Minus')
plt.legend(title='Team')
plt.grid(True)
plt.tight_layout()
plt.show()
