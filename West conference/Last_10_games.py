from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
import pandas as pd


team_names = ['Golden State Warriors', 'Memphis Grizzlies', 'Sacramento Kings', 'Dallas Mavericks']


all_teams = teams.get_teams()
team_ids = {team['full_name']: team['id'] for team in all_teams if team['full_name'] in team_names}


def get_last_10_games(team_id, team_name):
    gamelog = teamgamelog.TeamGameLog(team_id=team_id, season='2024-25', season_type_all_star='Regular Season')
    df = gamelog.get_data_frames()[0]
    df = df[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST']].head(10)
    df['TEAM'] = team_name
    return df


all_data = pd.concat([
    get_last_10_games(team_ids['Golden State Warriors'], 'Warriors'),
    get_last_10_games(team_ids['Memphis Grizzlies'], 'Grizzlies'),
    get_last_10_games(team_ids['Sacramento Kings'], 'Kings'),
    get_last_10_games(team_ids['Dallas Mavericks'], 'Mavericks')
])


print("Last 10 games stats：")
print(all_data)


print(all_data['MATCHUP'].unique())

# 胜率统计
summary = all_data.groupby(['TEAM', 'WL']).size().unstack(fill_value=0)
summary['WIN_RATE'] = summary['W'] / (summary['W'] + summary['L'])
print("\nWinRates：\n", summary)


