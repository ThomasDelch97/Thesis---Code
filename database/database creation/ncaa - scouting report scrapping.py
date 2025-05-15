## Configuration
import requests
import random
import time
import pandas as pd
from bs4 import BeautifulSoup, Comment
import re
from functools import reduce
from functions import fetch_html

# Precompile regex patterns for school_clean processing
CLEAN_PATTERN = re.compile(r"[()&.']")
SPACE_PATTERN = re.compile(r"\s+")

BASE_URL = "https://www.nbadraft.net/"
NAME_GATHERING = "search-players/?search_player=&schoolclass=senior%2Cjunior%2Csophomore%2Cfreshman"
REQUEST_DELAY = time.sleep(random.uniform(2, 5))  # Need to mimic human behaviour
dico_of_error = {}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL,
}
session = requests.Session()
session.headers.update(HEADERS)

## Scraping
ranking_url = BASE_URL + NAME_GATHERING    
try:
    ranking_html = fetch_html(ranking_url, session)
    if not ranking_html:
        continue

    soup = BeautifulSoup(ranking_html, 'lxml')
    table = soup.find('table')

    # Use direct table parsing if possible
    headers = []
    rows = []
    tbody = table.find('tbody') or table
    for row in tbody.find_all('tr'):
        cells = row.find_all('td')
        if cells:
            rows.append([cell.get_text(strip=True) for cell in cells])
        ranking = pd.DataFrame(rows, columns=headers)

    ranking["full_name"] = ranking['First Name'].str + ranking['Last Name'].str
    ranking["full_name"] = (
                    ranking["full_name"]
                    .str.replace(CLEAN_PATTERN, "-", regex=True)
                    .str.strip()
                    .str.lower()
                )
    
    for name in ranking["full_name"]: #Get every player scouting report and evaluation
         player_url = BASE_URL + f"https://www.nbadraft.net/players/{name}/"

        try:
            player_html = fetch_html(player_url, session)
            if not player_html:
                continue
            soup = BeautifulSoup(player_html, 'lxml')


            # Use direct table parsing if possible
            headers = []
            rows = []
            tbody = table.find('tbody') or table
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    rows.append([cell.get_text(strip=True) for cell in cells])
                ranking = pd.DataFrame(rows, columns=headers)
        
        except Exception as e:
            print(f"Error processing: {e}")
    
except Exception as e:
            print(f"Error processing: {e}")

    

            continue
for key, value in stats.items():
    for year in range(2006, 2026):
        
       

            
            
            
            
            

            if key == "school":
                # Optimized school cleaning with precompiled regex
                season_college_team['school_clean'] = (
                    season_college_team['School']
                    .str.replace(CLEAN_PATTERN, "", regex=True)
                    .str.replace(SPACE_PATTERN, "-", regex=True)
                    .str.replace(NCAA_PATTERN, "", regex=True)
                    .str.strip()
                    .str.lower()
                )

                school_dfs = []
                for j, school in enumerate(season_college_team['school_clean']):
                    print(f'{year} :', round(j/len(season_college_team), 3)*100, "%")
                    try:
                        player_url = BASE_URL + f'/cbb/schools/{school}/men/{year}.html'
                        player_html = fetch_html(player_url, session)
                        if not player_html:
                            continue

                        soup = BeautifulSoup(player_html, 'lxml')
                        tables = soup.find_all('table')
                        
                        # Extract tables from comments
                        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                        for comment in comments:
                            comment_soup = BeautifulSoup(comment, 'lxml')
                            tables.extend(comment_soup.find_all('table'))

                        # Determine table configuration
                        table_config = dic_of_position_1 if len(tables) == 9 else dic_of_position_2
                        exclude_pos = exclude_pos_1 if len(tables) == 9 else exclude_pos_2

                        dfs_to_merge = []
                        for i, table in enumerate(tables):
                            if i in exclude_pos:
                                continue
                            
                            # Extract headers and rows
                            header_row = table.find('thead').find('tr') if table.find('thead') else table.find('tr')
                            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                            
                            rows = []
                            tbody = table.find('tbody') or table
                            for row in tbody.find_all('tr'):
                                cells = row.find_all(['td', 'th'])
                                if cells:
                                    rows.append([cell.get_text(strip=True) for cell in cells])
                            
                            if not rows:
                                continue
                            
                            df = pd.DataFrame(rows, columns=headers)
                            if i == 0:
                                df['Team'] = school
                                dfs_to_merge.append(df)
                            else:
                                prefix = table_config.get(i, f'table_{i}')
                                df = df.add_prefix(f'{prefix}_').rename(columns={f'{prefix}_Player': 'Player'})
                                dfs_to_merge.append(df)

                        if dfs_to_merge:
                            # Efficient merge using reduce
                            teamly = reduce(
                                lambda left, right: pd.merge(left, right, on=['Player'], how='left', suffixes=('', '_drop')),
                                dfs_to_merge
                            )
                            teamly = teamly.loc[:, ~teamly.columns.str.endswith('_drop')]
                            school_dfs.append(teamly)

                    except Exception as e:
                        print(f"Error processing {school} ({year}): {e}")
                        dico_of_error[school] = str(year)

                if school_dfs:
                    yearly = pd.concat(school_dfs, ignore_index=True)
                    yearly.to_csv(f'Player NCAA {year}.csv', index=False)

        

print("Scraping completed with errors:", dico_of_error)