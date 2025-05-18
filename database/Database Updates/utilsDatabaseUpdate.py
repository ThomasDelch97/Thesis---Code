import pandas as pd

#Standardize player name for merging - delete all the unusefull things
def clean_player_name(name_series):
    return (
        name_series.str.lower()
        .str.strip()
        .str.replace(r'[\s\'\.]', '', regex=True)
    )

#Pivot the columns to create many target variables based on their year
def create_wide_table(df, values=None, team_markers=None):
    team_markers = team_markers or ['2TM', '3TM', '4TM', '5TM'] #When part of more than one team during a season
    values = values or ['WS', 'WS/48', 'MP', 'G'] #the targets that we want to try
    
    filtered = df[~df['Team'].isin(team_markers)]
    return filtered.pivot_table(
        index='player_id',
        columns='yrs',  #Make that the columns exist
        values=values,
        aggfunc='mean' #mean if player played in several teams
    ).pipe(lambda df: df.set_axis(
        [f'{stat}-{yr}' for stat, yr in df.columns], 
        axis=1
    )).reset_index()

def get_last_seasons(df):
    idx = df.groupby('player_id')['season'].idxmax() #Take only the last NCAA season of a player for its features
    return df.loc[idx]



#Generic class to handle player data processing
class updateDatabase:
    def __init__(self, df):
        self.df = df

    def add_first_season(self):
        #Add first_season column (min season per player)
        self.df['first_season'] = self.df.groupby('Player')['season'].transform('min')
        return self
    
    def add_draft_season(self, delay=1, correspondance=2000):
        #Add draft_season column (max season per player/team + 1 - 2000)
        self.df['draft_season'] = (
            self.df.groupby(['Player', 'Team'])['season'].transform('max') 
            + delay 
            - correspondance #Make the correspondance with NBA Data
        )
        return self
    
    def uidCreation(self, id_type='first_season', index=None):
        #Create player_id with optional season type
        try:   
            self.df['player_id'] = (
                clean_player_name(self.df['Player']) 
                + '_' 
                + self.df[id_type].astype(str).str[:index]
            )
        except:
            return "invalid column chosen"
        return self
        


def add_years_played(nba_data, draft_data):
    """
    Add 'yrs' column to nba_data indicating years played, where:
    - Players drafted BEFORE 2000 start at yrs=2 in 2000 season
    - Players drafted IN 2000 start at yrs=1 in their rookie season
    - Players drafted AFTER 2000 follow normal counting (yrs=1 in first season)
    """
    #Create a set of players drafted in 2000
    drafted_2000 = set(draft_data['Player'].unique())
    
    #Find all players and their first seasons
    player_first_season = nba_data.groupby('Player')['season'].min().to_dict()
    
    #Adjust first season for pre-2000 players
    for player, first_season in player_first_season.items():
        if player not in drafted_2000 and first_season == 1:
            #This player started before 2000 (since their first season is 2000-01)
            player_first_season[player] = 0  # Will make 2000 season count as yrs=2
    
    #Calculate years played
    nba_data['yrs'] = nba_data.apply(
        lambda row: row['season'] - player_first_season.get(row['Player'], row['season']) + 1,
        axis=1
    )
    
    return nba_data
    
    


