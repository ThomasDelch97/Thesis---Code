import requests
import time
import pandas as pd
from bs4 import BeautifulSoup, Comment
import re
from functools import reduce

#Precompile regex patterns for school_clean processing
CLEAN_PATTERN = re.compile(r"[()&.']")
SPACE_PATTERN = re.compile(r"\s+")
NCAA_PATTERN = re.compile(r"NCAA")

stats = {
    'advanced-school': 'Adv',
    'school': 'Avg',
    'opponent': 'Opps',
    'advanced-opponent': 'Adv-Opps',
}
BASE_URL = "https://www.sports-reference.com"
REQUEST_DELAY = 3.05  #Respecting 20 requests/minute rate limit
dico_of_error = {}
exclude_pos_1 = [1, 2, 3, 4, 6, 8, 10, 12]
exclude_pos_2 = [1, 2, 3, 4, 6, 8, 10, 11, 12, 14]
dic_of_position_1 = {0: "info", 5: "average", 7: "totals", 9: "per_40", 11: "advanced"}
dic_of_position_2 = {0: "info", 5: "average", 7: "totals", 9: "per_40", 13: "advanced"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": BASE_URL,
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)

def fetch_html(url, session):
    time.sleep(REQUEST_DELAY)  #Maintain rate limit
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

## Scraping
for key, value in stats.items():
    for year in range(2000, 2006):
        team_url = BASE_URL + f'/cbb/seasons/men/{year}-{key}-stats.html'
        try:
            team_html = fetch_html(team_url, session)
            if not team_html:
                continue

            soup = BeautifulSoup(team_html, 'lxml')
            table = soup.find('table')
            
            #Use direct table parsing if possible
            headers = ["School", "G", "W", "L", "W-L%", "SRS", "SOS", "del1",
                      "W", "L", "del2", "W", "L", "del3", "W", "L", "del4", 
                      "Tm.", "Opp.", "del5", "MP", "FG", "FGA", "FG%", "3P", 
                      "3PA", "3P%", "FT", "FTA", "FT%", "ORB", "TRB", "AST", 
                      "STL", "BLK", "TOV", "PF"]
            
            rows = []
            tbody = table.find('tbody') or table
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    rows.append([cell.get_text(strip=True) for cell in cells])

            season_college_team = pd.DataFrame(rows, columns=headers)
            season_college_team.to_csv(f'Team NCAA {year} {key}.csv', index=False)

            if key == "school":
                #Optimized school cleaning with precompiled regex
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
                        
                        #Extract tables from comments
                        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                        for comment in comments:
                            comment_soup = BeautifulSoup(comment, 'lxml')
                            tables.extend(comment_soup.find_all('table'))

                        #Determine table configuration
                        table_config = dic_of_position_1 if len(tables) == 9 else dic_of_position_2
                        exclude_pos = exclude_pos_1 if len(tables) == 9 else exclude_pos_2

                        dfs_to_merge = []
                        for i, table in enumerate(tables):
                            if i in exclude_pos:
                                continue
                            
                            #Extract headers and rows
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

        except Exception as e:
            print(f"Error processing {key} {year}: {e}")
            continue

print("Scraping completed with errors:", dico_of_error)