import pandas as pd
import time
from utilsDatabaseUpdate import updateDatabase, create_wide_table, get_last_seasons, add_years_played
from datetime import datetime

HOME = r"C:\Users\Utilisateur\Desktop\Master ULB\Mémoire\Database"
TARGET_PATH = r"\NBA\Stats 2000 to 2024\Regular Season.xlsx"
FEATURE_PATH = r"\Working db\Features\working_df_27-4-25.csv"

df1 = pd.read_excel(HOME + TARGET_PATH)
features =  pd.read_csv(HOME+FEATURE_PATH)
DRAFT_2000 = HOME + r"\NBA\Draft Picks 2000 to 2024\NBA Draft Picks 2000.csv"
draft = pd.read_csv(DRAFT_2000)

df1 = add_years_played(df1, draft)
col_interest = ['Player', 'Team', 'Pos', 'G', 'MP', 
        'WS', 'WS/48', 'WS_x', 'WS/48_x', 'season', 'yrs'] #Columns that might be target
target = df1[col_interest]
dic = {
    'WS' : 'WS_x',
    'WS/48' : 'WS/48_x'
}
for i, j in dic.items():
    target[i] = target[i].fillna(target[j])

#Process target data
target_processor = (
    updateDatabase(target)
    .add_first_season()
    .uidCreation('first_season', index=None)
)
target_df = target_processor.df
wide_df = create_wide_table(target_df)
#Process features data
features_processor = (
    updateDatabase(features)
    .add_draft_season()
    .uidCreation('draft_season', index=-2)
)
features_df = features_processor.df
last_seasons = get_last_seasons(features_df)
#Add suffixes
wide_df = wide_df.add_suffix('_target')  #suffixe for features part
last_seasons = last_seasons.add_suffix('_features')  #suffixe for target part
#Update 'player_id' to be able to merge
wide_df = wide_df.rename(columns={'player_id_target': 'player_id'})
last_seasons = last_seasons.rename(columns={'player_id_features': 'player_id'})

#Final merge
(pd.merge(wide_df, last_seasons, on='player_id')).to_excel(f'looping_df_{str(time.time())}.xlsx')