from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


team_names = ['Golden State Warriors', 'Memphis Grizzlies', 'Sacramento Kings', 'Dallas Mavericks']


all_teams = teams.get_teams()
team_ids = {team['full_name']: team['id'] for team in all_teams if team['full_name'] in team_names}


def get_games(team_id, team_name):
    gamelog = teamgamelog.TeamGameLog(team_id=team_id, season='2024-25', season_type_all_star='Regular Season')
    df = gamelog.get_data_frames()[0]
    df = df[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST']]
    df['TEAM'] = team_name
    return df


# Concatenate data for all teams
all_data = pd.concat([
    get_games(team_ids['Golden State Warriors'], 'Warriors'),
    get_games(team_ids['Memphis Grizzlies'], 'Grizzlies'),
    get_games(team_ids['Sacramento Kings'], 'Kings'),
    get_games(team_ids['Dallas Mavericks'], 'Mavericks')
])

# Pivot the table so that TEAM is the header
# 筛选出包含 GSW 和 MEM 的比赛数据
gsw_vs_mem_data = all_data[all_data['MATCHUP'].str.contains(r'GSW.*MEM|MEM.*GSW')]

# 删除重复的比赛日期
gsw_vs_mem_Wariorsdata = gsw_vs_mem_data[gsw_vs_mem_data['TEAM'] == 'Warriors']
gsw_vs_mem_Memphisdata = gsw_vs_mem_data[gsw_vs_mem_data['TEAM'] == 'Grizzlies']

Kings_vs_Mavs_data = all_data[all_data['MATCHUP'].str.contains(r'SAC.*DAL|DAL.*SAC')]
Kings_vs_Mavs_kingsdata = Kings_vs_Mavs_data[Kings_vs_Mavs_data['TEAM'] == 'Kings']
Kings_vs_Mavs_mavsdata = Kings_vs_Mavs_data[Kings_vs_Mavs_data['TEAM'] == 'Mavericks']



print("\nGSW vs MEM Data with TEAM as Header in all_data:")
print(gsw_vs_mem_Memphisdata)
print(gsw_vs_mem_Wariorsdata)
print("\nKings vs Mavs Data with TEAM as Header in all_data:")
print(Kings_vs_Mavs_kingsdata)
print(Kings_vs_Mavs_mavsdata)

