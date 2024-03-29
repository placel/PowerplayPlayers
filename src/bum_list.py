from fake_useragent import UserAgent
import requests
from datetime import date
import json
import pickle
import pandas
from bs4 import BeautifulSoup

PPP_LIMIT = 10
pp_map = dict()

CURRENT_SEASON = '20232024'

TEAM_ABBREVS = {
    'BOS': 'BOS',
    'BUF': 'BUF',
    'DET': 'DET',
    'FLA': 'FLA',
    'MTL': 'MON',
    'OTT': 'OTT',
    'TBL': 'TB',
    'TOR': 'TOR',
    'CAR': 'CAR',
    'CBJ': 'CBJ',
    'NJD': 'NJD',
    'NYI': 'NYI',
    'NYR': 'NYR',
    'PHI': 'PHI',
    'PIT': 'PIT',
    'WSH': 'WAS',
    'ARI': 'ARI',
    'CHI': 'CHI',
    'COL': 'COL',
    'DAL': 'DAL',
    'MIN': 'MIN',
    'NSH': 'NSH',
    'STL': 'STL',
    'WIN': 'WPG',
    'WPG': 'WPG',
    'ANA': 'ANH',
    'CGY': 'CGY',
    'EDM': 'EDM',
    'LAK': 'LA',
    'SJS': 'SJ',
    'VAN': 'VAN',
    'VGK': 'VGK',
    'SEA': 'SEA',
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

def write_to_csv(bum_list):
    df = pandas.DataFrame(bum_list)
    df.to_csv('./lib/ai_bum_list.csv', sep=',')

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
            #i['TEAM']['imageUrl'],
            i['TEAM'],
            i['PEN/GP'],
            i['PP%'],
            i['PK%'],
            i['G'],
            i['GA'],
        ]

        updated_team_list.append(temp)
    
    with open('./lib/teamList.json', 'w', encoding='utf-8') as f:
        json.dump(updated_team_list, f, ensure_ascii=False, indent=4)

    print('Wrote to json')

def display_bums(players, team_stats):

    for i in range(0, len(players)):
        players[i].update({'row': i})
    
    # print(df.to_markdown(tablefmt="grid"))
    # print(df.to_markdown(tablefmt="simple_grid"))
    # print(df.to_markdown(tablefmt="rounded_grid"))
    # print(df.to_markdown(tablefmt="fancy_grid"))
    # print(df.to_markdown(tablefmt="fancy_outline"))
    # print(df.to_markdown(tablefmt="double_outline"))
    # print(df.to_markdown(tablefmt="html"))
    df = pandas.DataFrame(players)
    print(df.to_markdown(tablefmt="heavy_outline"))

def get_team_stats():
    headers = { 'User-Agent': UserAgent().random }
    req = requests.get('https://www.statmuse.com/nhl/ask/nhl-penalties-per-game-by-team-2024', headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    rows = soup.find_all('tr')[1:] # Take all except the first row (is the table header)

    teams = []
    for i in rows:
        columns = i.find_all('td')

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


    all_players = soup.find_all('span', 'pname')

    filtered_players_name = []
    filtered_players_ppUnit = dict()

    game_list = soup.find_all('li', id='schedule-')
    team_abbrevs = []

    for g in game_list:
        temp_team_names = g.find_all('span', 'mascot')
        team_names = []
        for i in temp_team_names:
            team_names.append(str(i).split('">')[1].split('</span')[0])

        team_abbrevs.append(team_names)

    for p in all_players:
        first = str(p).split('class="pname">')[1]
        name = first.split('<span')[0].strip()
        spans = first.split('<span class="stats">', 2)

        ppUnit = ""
        for i in spans:
            if "PP" in i:
                ppUnit = i.split('</span')[0].replace('PP', '').strip()

        filtered_players_name.append(name)
        filtered_players_ppUnit[name.split('. ')[1][0:5].strip()] = ppUnit
    


    for i in range(0, len(players)):
        last_name = players[i]['skaterFullName'].split(' ', 1)[1].strip()

        abbrevName = str(players[i]['skaterFullName'][0]) + '. ' + str(''.join(last_name[0:5])) # Only use the last 5 letter of the players last name to avoid error like (R. Nugent-...)
        if abbrevName in ''.join(filtered_players_name):
            ppUnit = str(filtered_players_ppUnit[last_name[0:5].strip()])

            temp_player = players[i]
            temp_player.update({'ppUnit': ppUnit})

            # print(f'Player: {temp_player["teamAbbrevs"]}')
            playing_against = ''
            for i in team_abbrevs:
                temp_abbrev = temp_player['teamAbbrevs']
                split_abbrev = temp_abbrev.split(',')

                if len(split_abbrev) == 2:
                    temp_abbrev = split_abbrev[1]
                else:
                    temp_abbrev = split_abbrev[0]

                abbrev = TEAM_ABBREVS[temp_abbrev].lower()

                if str(abbrev) not in str(i):
                    continue

                if abbrev in str(i[0]):
                    playing_against = str(i[1]).upper()
                    break
                else:
                    playing_against = str(i[0]).upper()
                    break
                        
            temp_player.update({'vs': playing_against})
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
        print(START_URL + f'start={index}00&limit={index + 1}00' + END_URL)
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


    team_stats = get_team_stats()
    display_bums(bum_list, team_stats)
    # display_bums(bum_list)

    # players = rotogrinders(players)
    # players = get_pp_toi(players)
    # team_stats = get_team_stats()
    # display_bums(players, team_stats=team_stats)
    write_to_csv(bum_list)
    write_to_json(bum_list, team_stats)

    return bum_list

# if __name__ == '__main__':
#     pickle_open = open('bum_list', 'rb')
#     players = pickle.load(pickle_open)
#     get_bum_list(players)