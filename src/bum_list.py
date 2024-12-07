from fake_useragent import UserAgent
import requests
from datetime import date, datetime
import json
import pickle
import pandas
from bs4 import BeautifulSoup

PPP_LIMIT = 100
pp_map = dict()

CURRENT_SEASON = '20242025'

TEAM_ABBREVS = {
    'BOS': 'BOS',
    'BUF': 'BUF',
    'DET': 'DET',
    'FLA': 'FLA',
    'MTL': 'MON',
    'OTT': 'OTT',
    'TBL': 'TBL',
    'TOR': 'TOR',
    'CAR': 'CAR',
    'CBJ': 'CBJ',
    'NJD': 'NJD',
    'NYI': 'NYI',
    'NYR': 'NYR',
    'PHI': 'PHI',
    'PIT': 'PIT',
    'WSH': 'WSH',
    'ARI': 'ARI',
    'CHI': 'CHI',
    'COL': 'COL',
    'DAL': 'DAL',
    'MIN': 'MIN',
    'NSH': 'NSH',
    'STL': 'STL',
    'WIN': 'WPG',
    'WPG': 'WPG',
    'ANA': 'ANA',
    'CGY': 'CGY',
    'EDM': 'EDM',
    'LAK': 'LAK',
    'SJS': 'SJS',
    'VAN': 'VAN',
    'VGK': 'VGK',
    'SEA': 'SEA',
    'CLS': 'CBJ',
    'LA': 'LAK',
    'SJ': 'SJS',
    'TB': 'TBL',
    'WAS': 'WSH',
    'MON': 'MTL',
    'MTL': 'MTL',
    'ANH': 'ANA',
    'NJ': 'NJD',
    'UTA': 'UTA'
}

TEAMS_TO_ABBREV = {
    'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF',
    'Detroit Red Wings': 'DET',
    'Florida Panthers': 'FLA',
    'Montreal Canadiens': 'MTL',
    'Ottawa Senators': 'OTT',
    'Tampa Bay Lightning': 'TBL',
    'Toronto Maple Leafs': 'TOR',
    'Carolina Hurricanes': 'CAR',
    'Columbus Blue Jackets': 'CBJ',
    'New Jersey Devils': 'NJD',
    'New York Islanders': 'NYI',
    'New York Rangers': 'NYR',
    'Philadelphia Flyers': 'PHI',
    'Pittsburgh Penguins': 'PIT',
    'Washington Capitals': 'WSH',
    'Arizona Coyotes': 'ARI',
    'Chicago Blackhawks': 'CHI',
    'Colorado Avalanche': 'COL',
    'Dallas Stars': 'DAL',
    'Minnesota Wild': 'MIN',
    'Nashville Predators': 'NSH',
    'St. Louis Blues': 'STL',
    'Winnipeg Jets': 'WPG',
    'Anaheim Ducks': 'ANA',
    'Calgary Flames': 'CGY',
    'Edmonton Oilers': 'EDM',
    'Los Angeles Kings': 'LAK',
    'San Jose Sharks': 'SJS',
    'Vancouver Canucks': 'VAN',
    'Vegas Golden Knights': 'VGK',
    'Seattle Kraken': 'SEA',
    'Utah Hockey Club': 'UTA'
}

ABBREV_TO_TEAMS = {
    'BOS': 'Boston Bruins',
    'BUF': 'Buffalo Sabres',
    'DET': 'Detroit Red Wings',
    'FLA': 'Florida Panthers',
    'MTL': 'Montreal Canadiens',
    'OTT': 'Ottawa Senators',
    'TBL': 'Tampa Bay Lightning',
    'TOR': 'Toronto Maple Leafs',
    'CAR': 'Carolina Hurricanes',
    'CBJ': 'Columbus Blue Jackets',
    'NJD': 'New Jersey Devils',
    'NYI': 'New York Islanders',
    'NYR': 'New York Rangers',
    'PHI': 'Philadelphia Flyers',
    'PIT': 'Pittsburgh Penguins',
    'WSH': 'Washington Capitals',
    'ARI': 'Arizona Coyotes',
    'CHI': 'Chicago Blackhawks',
    'COL': 'Colorado Avalanche',
    'DAL': 'Dallas Stars',
    'MIN': 'Minnesota Wild',
    'NSH': 'Nashville Predators',
    'STL': 'St. Louis Blues',
    'WPG': 'Winnipeg Jets',
    'ANA': 'Anaheim Ducks',
    'CGY': 'Calgary Flames',
    'EDM': 'Edmonton Oilers',
    'LAK': 'Los Angeles Kings',
    'SJS': 'San Jose Sharks',
    'VAN': 'Vancouver Canucks',
    'VGK': 'Vegas Golden Knights',
    'SEA': 'Seattle Kraken',
    'UTA': 'Utah Hockey Club'
}

# Filters through all the players retrieved from NHL API to find the players with less ppPoints than the PP_LIMIT
def filter_pp(players):
    for p in players:
        if p['ppPoints'] <= PPP_LIMIT:
            pp_map[p['skaterFullName']] = {
                    'skaterFullName': p['skaterFullName'],
                    'ppPoints': p['ppPoints'],
                    'teamAbbrevs': p['teamAbbrevs'],
                    #'assists': p['assists'],
                    'gamesPlayed': p['gamesPlayed'],
                    #'plusMinus': p['plusMinus'],
                    #'points': p['points'],
                    #'pointsPerGame': p['pointsPerGame'],
                    #'ppGoals': p['ppGoals'],
                    #'timeOnIcePerGame': p['timeOnIcePerGame'],
                    'shoots': p['shootsCatches'],
                    'position': p['positionCode']
                }
    
# Contains AI csv data
def write_to_csv(bum_list, team_stats):
    df_bl = pandas.DataFrame(bum_list)
    print(df_bl)
    team_stats = pandas.DataFrame(team_stats)
    
    # Remove the whitespace from the every column column
    team_stats = team_stats.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    # print(team_stats)
    # Replace the formal name (Toronto Maple Leafs) with abbreviation (TOR) for ease of access in the next few lines
    team_stats['TEAM'] = team_stats['TEAM'].map(TEAMS_TO_ABBREV)

    # the stats for the team the player is on and the team the playing is going against
    team = team_stats[team_stats['TEAM'].isin(df_bl['teamAbbrevs'])].copy()
    enemy = team_stats[team_stats['TEAM'].isin(df_bl['vs'])].copy()  

    team_rename = {
        'PEN/GP': 'team_PEN/GP',
        'PP%': 'team_PP%',
        'PK%': 'team_PK%',
        'G':  'team_G',
        'GA': 'team_GA'
    }

    enemy_rename = {
        'PEN/GP': 'enemy_PEN/GP',
        'PP%': 'enemy_PP%',
        'PK%': 'enemy_PK%',
        'G':  'enemy_G',
        'GA': 'enemy_GA'
    }

    # Rename columns so there are no duplicates
    team.rename(columns=team_rename, inplace=True)
    enemy.rename(columns=enemy_rename, inplace=True)

    # Add the Date column for when the 'data_collection.py' script is run
    df_bl['date'] = date.today().strftime('%Y-%m-%d')
    
    # # Generated by ChatGPT; This keeps the data in 1 row after concatenation instead of 3 rows
    df_bl.reset_index(drop=True, inplace=True)
    team.reset_index(drop=True, inplace=True)
    enemy.reset_index(drop=True, inplace=True)

    df1 = pandas.DataFrame(df_bl)
    df2 = pandas.DataFrame(team)
    df3 = pandas.DataFrame(enemy)

    # Generated by ChatGPT
    # Merge the DataFrames based on specified conditions
    merged_df = df1.merge(df2, how='left', left_on='teamAbbrevs', right_on='TEAM', suffixes=('', '_team')).merge(df3, how='left', left_on='vs', right_on='TEAM', suffixes=('', '_enemy'))

    # Drop redundant columns
    merged_df.drop(columns=['TEAM', 'TEAM_enemy'], inplace=True)

    # Add the 'scored' column which will be updated by data_collection.py
    merged_df['scored'] = 0

    merged_df.to_csv('./lib/ai_bum_list.csv', sep=',', index=False)

def write_to_json(bum_list, team_list):

    # Format the json for index.html use
    updated_bum_list = []
    for i in bum_list:
        temp_abbrev = i['teamAbbrevs']
        split_abbrev = temp_abbrev.split(',')

        # Handles 2 abbrevs in one, example: "TOR, OTT" where the player was on Toronto but was recently traded and is now on Ottawa, and hasn't been fully updated yet  
        if len(split_abbrev) == 2:
            temp_abbrev = split_abbrev[1].strip()
        else:
            temp_abbrev = split_abbrev[0].strip()

        # Used to differentiate between Centers, Leftwing, Rightwing, and Defencemen
        position = str(i['position'])
        if 'L' in position or 'R' in position:
            position += "W"

        temp = [
            str(i['skaterFullName']),
            str(TEAM_ABBREVS[temp_abbrev]),
            str(i['ppPoints']),
            str(i['ppUnit']),
            str(position),
            str(i['gamesPlayed']),
            str(i['avgPowerplayToi']),
            str(i['vs'])
        ]

        updated_bum_list.append(temp)

    with open('./lib/bumList.json', 'w', encoding='utf-8') as f:
        json.dump(updated_bum_list, f, ensure_ascii=False, indent=4)

    updated_team_list = []
    for i in team_list:
        temp = [
            str(i['TEAM']).strip(),
            str(i['PEN/GP']).strip(),
            str(i['PP%']).strip(),
            str(i['PK%']).strip(),
            str(i['G']).strip(),
            str(i['GA']).strip(),

            str(i['PPGA']).strip(),
            str(i['PPGF']).strip(),
            str(i['PPG/PG']).strip(),
            str(i['PPO/PG']).strip(),
            str(i['PPTOI/PG']).strip(),
            str(i['PEN']).strip(),
            str(i['PENMin']).strip(),
            str(i['PENSeconds/PG']).strip(),
            str(i['PENDrawn/GP']).strip(),
            str(i['PKTIO/PG']).strip(),
        ]

        updated_team_list.append(temp)
    
    with open('./lib/teamList.json', 'w', encoding='utf-8') as f:
        json.dump(updated_team_list, f, ensure_ascii=False, indent=4)

    print('Wrote to json')

def display_bums(players, team_stats):

    for i in range(0, len(players)):
        players[i].update({'row': i})

    df = pandas.DataFrame(players)
    print(df.to_markdown(tablefmt="heavy_outline"))

# Deprecated: statmuse needs a subscription now
def statmuse_get_team_stats():
    headers = { 'User-Agent': UserAgent().random }
    req = requests.get('https://www.statmuse.com/nhl/ask/nhl-penalties-per-game-by-team-2024', headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    rows = soup.find_all('tr')[1:] # Take all except the first row (is the table header)

    teams = []
    for i in rows:
        columns = i.find_all('td')
        print(i)
        team = {
            'TEAM': columns[0].text,
            'PEN/GP': columns[3].text,
            'PP%': columns[12].text,
            'PK%': columns[13].text,
            'G': columns[10].text,
            'GA': columns[11].text
        }

        teams.append(team)

    return teams

def nhl_get_team_stats():
    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22wins%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C={CURRENT_SEASON}%20and%20seasonId%3E={CURRENT_SEASON}'
    req = requests.get(url, headers=headers)

    team_data = json.loads(req.content)['data']

    teams = []
    for i in team_data:
        teams.append({
            'TEAM': i['teamFullName'],
            'G': i['goalsFor'],
            'GA': i['goalsAgainst']
        })
    
    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.nhle.com/stats/rest/en/team/powerplay?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22powerPlayPct%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C={CURRENT_SEASON}%20and%20seasonId%3E={CURRENT_SEASON}'
    req = requests.get(url, headers=headers)

    team_powerplay_data = json.loads(req.content)['data']

    for i in team_powerplay_data:
        for team in teams:
            if team['TEAM'] == i['teamFullName']:
                team['PP%'] = i['powerPlayPct']
                team['PPGF'] = i['powerPlayGoalsFor']
                team['PPG/PG'] = i['ppGoalsPerGame']
                team['PPO/PG'] = i['ppOpportunitiesPerGame']
                team['PPTOI/PG'] = i['ppTimeOnIcePerGame']

                break
    
    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.nhle.com/stats/rest/en/team/penalties?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22penaltyMinutes%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C={CURRENT_SEASON}%20and%20seasonId%3E={CURRENT_SEASON}'
    req = requests.get(url, headers=headers)
    
    team_penalty_data = json.loads(req.content)['data']

    for i in team_penalty_data:
        for team in teams:
            if team['TEAM'] == i['teamFullName']:
                team['PEN'] = i['penalties']
                team['PENMin'] = i['penaltyMinutes']
                team['PEN/GP'] = i['penaltiesTakenPer60']
                team['PENSeconds/PG'] = i['penaltySecondsPerGame']
                team['PENDrawn/GP'] = i['penaltiesDrawnPer60']

                break

    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.nhle.com/stats/rest/en/team/penaltykill?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22penaltyKillPct%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C={CURRENT_SEASON}%20and%20seasonId%3E={CURRENT_SEASON}'
    req = requests.get(url, headers=headers)

    team_penalty_kill_data = json.loads(req.content)['data']

    for i in team_penalty_kill_data:
        for team in teams:
            if team['TEAM'] == i['teamFullName']:
                team['PPGA'] = i['ppGoalsAgainst']
                team['PK%'] = i['penaltyKillPct']
                team['PKTIO/PG'] = i['pkTimeOnIcePerGame']

                break

    for i in teams:
        if 'é' in i['TEAM']:
            i['TEAM'] = i['TEAM'].replace('é', 'e') 

    return teams

# https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
def convert_seconds(seconds):
    if seconds == 'N/A':
        return 'N/A'
    
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%02d:%02d" % (minutes, seconds)

def multiples_found(soup, player):
    headers = { 'User-Agent': UserAgent().random }

    BASE_URL = 'https://www.quanthockey.com'

    # TODO: Add functionality in case multiple matches found even after position and shooting style
    if player['skaterFullName'] == 'Mike Hoffman':
        return False

    if player['skaterFullName'] == 'Mike Matheson':
        return False
    
    if player['skaterFullName'] == 'Nicholas Paul':
        return False

    player_bio = ''

    if player['position'] == 'C' or player['position'] == 'R' or player['position'] == 'L':
        player_bio += 'Forward, '
    else:
        player_bio += 'Defenseman, '

    if player['shoots'] == 'R':
        player_bio += 'shoots right'
    else:
        player_bio += 'shoots left'

    all_player = soup.find('table', id='statistics').find_all('tr')
    player_links = []
    soup = ''
    for i in range(1, len(all_player)):
        player_links.append(BASE_URL + all_player[i].find('a')['href'])

    for i in player_links:
        req = requests.get(i, headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')

        bio = soup.find('div', id='player-bio')
        name_field = soup.find('h1', id='pp_title').text
        if player_bio in bio and player['skaterFullName'].split(' ', 1)[1] in name_field:
            break

    # Return soup with the proper page data
    return soup
 
def get_pp_toi(players):

    # If getting the average of the last 5 games; grab url of player to get the player id, then go to that url and use the 'Last 5 NHL Games' table
    headers = { 'User-Agent': UserAgent().random }

    PLAYER_URL = f'https://www.quanthockey.com/player-search.php?q='

    # YEAR = date.today()
    last_5 = ''
    new_players = []

    count = 0
    for p in players:
        count += 1
        print(f'Progress: ({count}/{len(players)}): {round((count/len(players) * 100))}%', end='\r')
        all_pp_toi = []

        # 2 players have the same name, so we need to differentiate between them
        if p['skaterFullName'] == 'Zach Benson':
            p['skaterFullName'] = 'Zachary Benson'
            
        req = requests.get('https://www.quanthockey.com/player-search.php?q=' + str(p['skaterFullName']), headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')

        # Check if the couldn't be found because of a duplicate
        try:
            last_5 = soup.find('table', id='lg_stats').find_all('tr')
        except:
            soup = multiples_found(soup, p) # Returns false if player could not be found, otherwise return bs4 soup with current page data

            if not soup:
                continue
            
            try:
                last_5 = soup.find('table', id='lg_stats').find_all('tr')
            except:
                continue
        
        # Goes though each row of the table, skipping the first and last (useless) and grabs the pp_toi from the 9th index of the 42 item long list of td
        for i in range(1, len(last_5) -1):
            cols = last_5[i].find_all('td')
            
            index = 0
            for k in cols:
                index += 1
                if index == 9:
                    time = k.text
                    
                    try:
                        m, s = time.split(':')
                        time = int(m) * 60 + int(s)

                        all_pp_toi.append(int(time))
                    except:
                        all_pp_toi.append('N/A')

                    break
        
        if 'N/A' not in all_pp_toi:
            average_pp_toi = 0
            for i in all_pp_toi:
                average_pp_toi += i

            # Handle dividing by 0 error
            try:
                average_pp_toi /= 5
            except:
                average_pp_toi = 0
        else:
            average_pp_toi = 'N/A'

        temp_player = p
        temp_player.update({'avgPowerplayToi': convert_seconds(average_pp_toi)})
        new_players.append(temp_player)

    return new_players 

def rotogrinders(players):
    headers = { 'User-Agent': UserAgent().random }
    
    pp_links = []
    new_players = []

    req = requests.get('https://rotogrinders.com/lineups/nhl#', headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')


    player_info = soup.find_all('div', 'player-nameplate-info')

    filtered_players_name = []
    filtered_players_ppUnit = dict()

    game_list = soup.find_all('div', class_='game-card')
    team_abbrevs = []

    # Extract the team names
    for g in game_list:
        temp_team_names = g.find_all('span', class_='team-nameplate-title')
        team_names = []
        for i in temp_team_names:
            name = f"{i.find('span', class_='team-nameplate-city').get_text().strip()} {i.find('span', class_='team-nameplate-mascot').get_text().strip()}"
            # team_names.append(str(i).split('">')[1].split('</span')[0])
            team_names.append(name.upper())

        team_abbrevs.append(team_names)

    # print(team_abbrevs)
    # team_abbrevs.pop(len(team_abbrevs) - 1)

    for i, p in enumerate(player_info):

        # If the player is a goalie, go next as we don't want goalie info
        position = p.find('span', class_='small muted').get_text()
        if position == 'G':
            continue

        # Extract player name, and powerplay unit
        name = p.find('a', class_='player-nameplate-name')
        if name:
            name = name.get_text().strip()
        else:
            continue # If the player is greyed out on the site, don't account for them, and go to next

        
        # Check if player is on a powerplay unit or not. If not, set value to -1 to weed out later
        ppUnit = p.find('span', class_='small bold red')
        if ppUnit:
            ppUnit = ppUnit.get_text().replace('PP', '').strip()
        else:
            ppUnit = -1

        # print(f'{name} is on powerplay unit {ppUnit}')

        # Append the player info to respective list
        filtered_players_name.append(name)
        filtered_players_ppUnit[name] = ppUnit

    for i in range(0, len(players)):
        name = players[i]['skaterFullName'].strip()

        # abbrevName = str(players[i]['skaterFullName'][0]) + '. ' + str(''.join(last_name[0:5])) # Only use the last 5 letter of the players last name to avoid error like (R. Nugent-...)
        if name in ''.join(filtered_players_name):
            ppUnit = str(filtered_players_ppUnit[name.strip()])

            temp_player = players[i]
            temp_player.update({'ppUnit': ppUnit})
            
            if name == 'Elias Lindholm':
                continue
            
            playing_against = ''
            for k in team_abbrevs:
                temp_abbrev = temp_player['teamAbbrevs']
                split_abbrev = temp_abbrev.split(',')

                if len(split_abbrev) == 2:
                    temp_abbrev = split_abbrev[1]
                else:
                    temp_abbrev = split_abbrev[0]


                abbrev = TEAM_ABBREVS[temp_abbrev]

                # Get the teams abreviation
                try:
                    k[0] = TEAMS_TO_ABBREV[k[0].title()]
                    k[1] = TEAMS_TO_ABBREV[k[1].title()]
                except:
                    k[0] = TEAM_ABBREVS[k[0].upper()]
                    k[1] = TEAM_ABBREVS[k[1].upper()]
                
                if str(abbrev) not in str(k):
                    continue
                
                if abbrev in str(k[0]):
                    playing_against = TEAM_ABBREVS[str(k[1]).upper()]
                    break
                else:
                    playing_against = TEAM_ABBREVS[str(k[0]).upper()]
                    break
            
            temp_player.update({'vs': TEAM_ABBREVS[playing_against]})
            new_players.append(temp_player)
    
    return new_players

def get_bum_list(players):
    bum_list = []
    YEAR = date.today().strftime('%y')
    START_URL = f'https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22%3A%22ppPoints%22,%22direction%22%3A%22DESC%22%7D,%7B%22property%22%3A%22playerId%22,%22direction%22%3A%22ASC%22%7D%5D&'
    END_URL = f'&factCayenneExp=gamesPlayed%3E%3D1&cayenneExp=gameTypeId%3D2%20and%20seasonId%3C%3D{CURRENT_SEASON}%20and%20seasonId%3E%3D{CURRENT_SEASON}'
    UserAgent().random

    all_players = []
    index = 0
    while True:
        # print(START_URL + f'start={index}00&limit={index + 1}00' + END_URL)
        req = requests.get(START_URL + f'start={index}00&limit={index + 1}00' + END_URL) # Grabs a list of players; Place index number inside url to creat limits like 200 - 300 whn index is 2
        current = json.loads(req.content)['data']
        all_players += current
        index += 1

        # If no more players are returned through the URL, break        
        if len(current) == 0:
            break
    
    filter_pp(all_players)
    for i in players:
        if i.replace('ö', 'o').strip() in pp_map.keys(): # replace is for Emil Bemstrom
            player = pp_map[i.replace('ö', 'o').strip()]
            bum_list.append(player)
    
    with open('./lib/bum_list.pickle', 'wb') as f:
        pickle.dump(bum_list, f)
        print('Wrote to bum_list')

    
    bum_list = rotogrinders(bum_list)
    bum_list = get_pp_toi(bum_list)

    # team_stats = statmuse_get_team_stats() # Deprecated : statmuse needs a subscription now
    team_stats = nhl_get_team_stats()
    display_bums(bum_list, team_stats)
    # display_bums(bum_list)

    # players = rotogrinders(players)
    # players = get_pp_toi(players)
    # team_stats = get_team_stats()
    # display_bums(players, team_stats=team_stats)
    # write_to_csv(bum_list, team_stats)
    write_to_json(bum_list, team_stats)

    return bum_list

# if __name__ == '__main__':
#     pickle_open = open('lib/bum_list.pickle', 'rb')
#     players = pickle.load(pickle_open)
#     get_bum_list(players)