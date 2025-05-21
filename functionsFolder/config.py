#Unstructured data
text_data = [
    "Class", #Dummy 
    "Pos_x", #Dummy
    "average_Awards", #Dummy & flag
    "Strength", #Scouting report
    "Weakness", #Scouting report
    "RSCI Top 100", #Rankings represent the player's final standing within his high school class in a given year/Dummy
]
#Biometric data that I will use
biometric_data = [
    "Height", #Won't change
    "Weight", #Won't change
    "Draft_pos", #Proxy ?
]
#Everything that I want to delete
adv_to_del = [
    "advanced_Awards", "totals_PER", "totals_TS%", "totals_3PAr",	"totals_FTr", "totals_PProd", "totals_ORB%", "totals_DRB%", "totals_TRB%", "totals_AST%", "totals_STL%", "totals_BLK%", "totals_TOV%", "totals_USG%", "totals_OWS", "totals_DWS", "totals_WS", "totals_WS/40", "totals_OBPM", "totals_DBPM", "totals_BPM",
	"G", "MP", "FG", "FGA", "FG%", "2P", "2PA",	"2P%", "3P", "3PA",	"3P%", "FT", "FTA",	"FT%", "ORB", "DRB", "TRB",	"AST", "STL", "BLK", "TOV",	"PF", "PTS"
]
team_to_del = [
    "G_opp", "W_opp", "L_opp", "W-L%_opp", "SRS_opp", "SOS_opp", "W.1_opp", "L.1_opp", 
    "W.2_opp", "L.2_opp", "W.3_opp", "L.3_opp", "Tm._opp", "Opp._opp", "MP_opp" #Just a replicate of the other part from team
]
id = [
    "UID_scout", #Won't use
    "team_for_merging", #Won't use
    "Name_for_merging", #Won't use
    "Name" #Won't use
]
useless = [
    "player_id",
    "Player",	
    "Unnamed: 0.1",	
    "Unnamed: 0",
    "Summary", 
    "average_Rk", 
    "average_Pos",
    "#", #Uniform number
    "totals_Rk", "per_40_Rk",
    "totals_Pos", "totals_G", "totals_GS",
    "per_40_Pos", "per_40_G", "per_40_GS",
    "totals_MP", "per_40_MP",
    "Unnamed: 0_team",
    "Unnamed: 24", 
    "Unnamed: 140",
    "advanced_Rk", "advanced_Pos", "advanced_G", "advanced_GS", "advanced_MP",
    "Pos_y",
    "totals_Awards",
    "per_40_Awards",
    "del1", "del2", "del3", "del4", "del5", 
    "del1_opp", "del2_opp", "del3_opp", "del4_opp", "del5_opp",
    "UID_scout", #Won't use
    "team_for_merging", #Won't use
    "Name_for_merging", #Won't use
    "Name", #Won't use
    "G_opp", "W_opp", "L_opp", "W-L%_opp", "SRS_opp", "SOS_opp", "W.1_opp", "L.1_opp", 
    "W.2_opp", "L.2_opp", "W.3_opp", "L.3_opp", "Tm._opp", "Opp._opp", "MP_opp",
    "advanced_Awards", "totals_PER", "totals_TS%", "totals_3PAr",	"totals_FTr", "totals_PProd", "totals_ORB%", "totals_DRB%", "totals_TRB%", "totals_AST%", "totals_STL%", "totals_BLK%", "totals_TOV%", "totals_USG%", "totals_OWS", "totals_DWS", "totals_WS", "totals_WS/40", "totals_OBPM", "totals_DBPM", "totals_BPM",
	"G", "MP", "FG", "FGA", "FG%", "2P", "2PA",	"2P%", "3P", "3PA",	"3P%", "FT", "FTA",	"FT%", "ORB", "DRB", "TRB",	"AST", "STL", "BLK", "TOV",	"PF", "PTS",
    "height", #Won't use
    "Ht", #From scouting
    "Wt", #From scouting
    "season", #Won't use
    "draft_season", #Won't use 
    "Draft_Year", #Won't use
    "Grade", #Dummy (Same as above: won't use)
    "Hometown", #Won't use/or international?
    "Team", #won't use
    "High School", #Won't use
    "School", #School from team NCAA data
    "College" #From scouting
]
index = ["Player"]
#Past stats interesting to keep 
to_keep = {
    "avg" : ["average_G", "average_GS", "average_MP", "average_FG", "average_FGA", "average_FG%", "average_3P", "average_3PA", "average_3P%", "average_2P", "average_2PA", "average_2P%", "average_eFG%", "average_FT", "average_FTA", "average_FT%", "average_ORB", "average_DRB", "average_TRB", "average_AST", "average_STL", "average_BLK", "average_TOV", "average_PF", "average_PTS"],		#OK c'est good
    "tot" : ["totals_FG", "totals_FGA",	"totals_FG%", "totals_3P", "totals_3PA", "totals_3P%", "totals_2P",	"totals_2PA", "totals_2P%",	"totals_eFG%", "totals_FT",	"totals_FTA", "totals_FT%",	"totals_ORB", "totals_DRB",	"totals_TRB", "totals_AST",	"totals_STL", "totals_BLK", "totals_TOV", "totals_PF", "totals_PTS"], #OK c'est good
    "per_40" : ["per_40_FG", "per_40_FGA", "per_40_FG%", "per_40_3P", "per_40_3PA",	"per_40_3P%", "per_40_2P", "per_40_2PA", "per_40_2P%", "per_40_eFG%", "per_40_FT", "per_40_FTA", "per_40_FT%", "per_40_ORB", "per_40_DRB", "per_40_TRB", "per_40_AST", "per_40_STL", "per_40_BLK", "per_40_TOV", "per_40_PF", "per_40_PTS"], #OK c'est good
    "scouting_reports" : ["Athleticism", "Size", "Defense", "Strength2", "Quickness", "Leadership", "Jump Shot", "NBA Ready", "Rebounding", "Potential", "Post Skills", "Intangibles"], #OK perfect
    "team" : ["G_team", "W", "L", "W-L%", "SRS", "SOS", #SRS=Simple Rating System
              "W.1", "L.1", "W.2", "L.2", "W.3", "L.3", "Tm.", "Opp.", #1=Conf, 2=Home, 3=Away, Tm./Opp.=Number of points
              "MP_team", "FG_team", "FGA_team", "FG%_team", "3P_team", "3PA_team", "3P%_team", "FT_team", "FTA_team", "FT%_team", "ORB_team", "TRB_team", "AST_team", "STL_team", "BLK_team", "TOV_team", "PF_team"], #How the team behaved, in term of total
    "opp" : ["FG_opp", "FGA_opp", "FG%_opp", "3P_opp", "3PA_opp", "3P%_opp", "FT_opp", "FTA_opp", "FT%_opp", "ORB_opp",	"TRB_opp", "AST_opp", "STL_opp", "BLK_opp",	"TOV_opp", "PF_opp"], #How the opponent team behaved (in term of total)
    "adv" : ["advanced_PER", "advanced_TS%", "advanced_3PAr", "advanced_FTr", "advanced_PProd", "advanced_ORB%", "advanced_DRB%", "advanced_TRB%", "advanced_AST%", "advanced_STL%", "advanced_BLK%", "advanced_TOV%", "advanced_USG%", "advanced_OWS", "advanced_DWS", "advanced_WS", "advanced_WS/40", "advanced_OBPM", "advanced_DBPM", "advanced_BPM"]

}

#Add '_features' to all my columns from the dictionnaries
id = [s + '_features' for s in id] #deleted
team_to_del = [s + '_features' for s in team_to_del] #deleted
adv_to_del = [s + '_features' for s in adv_to_del] #deleted
biometric_data = [s + '_features' for s in biometric_data] 
text_data = [s + '_features' for s in text_data] 
for key in to_keep:
    to_keep[key] = [s + '_features' for s in to_keep[key]]
for count, word in enumerate(useless): #deleted
    try:
        useless[count] = word + '_features'
    except:
        continue