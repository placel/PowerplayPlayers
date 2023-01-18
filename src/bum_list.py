from fake_useragent import UserAgent
import requests
from datetime import date
import json
import pickle
import pandas
from bs4 import BeautifulSoup

PPP_LIMIT = 4
pp_map = dict()

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

def display_bums(players):
    df = pandas.DataFrame(players)
    
    # print(df.to_markdown(tablefmt="grid"))
    # print(df.to_markdown(tablefmt="simple_grid"))
    # print(df.to_markdown(tablefmt="rounded_grid"))
    # print(df.to_markdown(tablefmt="fancy_grid"))
    # print(df.to_markdown(tablefmt="fancy_outline"))
    # print(df.to_markdown(tablefmt="double_outline"))
    # print(df.to_markdown(tablefmt="html"))
    print(df.to_markdown(tablefmt="heavy_outline"))

# https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%02d:%02d" % (minutes, seconds)

def multiples_found(soup, player):
    headers = { 'User-Agent': UserAgent().random }

    BASE_URL = 'https://www.quanthockey.com'
    print('Multiple Found: ' + player['skaterFullName'])
    if player['skaterFullName'] == 'Mike Hoffman':
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

        if player_bio in bio:
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

    for p in players:
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

            last_5 = soup.find('table', id='lg_stats').find_all('tr')
        
        # Goes though each row of the table, skipping the first and last (useless) and grabs the pp_toi from the 9th index of the 42 item long list of td
        for i in range(1, len(last_5) -1):
            cols = last_5[i].find_all('td')
            
            index = 0
            for k in cols:
                index += 1
                if index == 9:
                    time = k.text
                    m, s = time.split(':')
                    time = int(m) * 60 + int(s)

                    all_pp_toi.append(int(time))
                    break
        
        average_pp_toi = 0
        for i in all_pp_toi:
            average_pp_toi += i

        # Handle dividing by 0 error
        try:
            average_pp_toi /= 5
        except:
            average_pp_toi = 0

        temp_player = p
        temp_player.update({'avgPowerplayToi': convert_seconds(average_pp_toi)})
        new_players.append(temp_player)

    return new_players 

def rotogrinders(players):
    headers = { 'User-Agent': UserAgent().random }
    
    pp_links = []
    new_players = []

    req = requests.get('https://rotogrinders.com/lineups/nhl?site=draftkings', headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    all_players = soup.find_all('span', 'pname')
    filtered_players_name = []
    filtered_players_ppUnit = dict()

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
            
            new_players.append(temp_player)
    
    return new_players

def get_bum_list(players):
    bum_list = []
    YEAR = date.today().strftime('%y')
    START_URL = f'https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22%3A%22ppPoints%22,%22direction%22%3A%22DESC%22%7D,%7B%22property%22%3A%22playerId%22,%22direction%22%3A%22ASC%22%7D%5D&'
    END_URL = f'&factCayenneExp=gamesPlayed%3E%3D1&cayenneExp=gameTypeId%3D2%20and%20seasonId%3C%3D20222023%20and%20seasonId%3E%3D20222023'
    UserAgent().random

    all_players = []
    index = 0
    while True:
        req = requests.get(START_URL + f'start={index}00&limit={index + 1}00' + END_URL) # Grabs a list of players; Place index number inside url to creat limits like 200 - 300 whn index is 2
        current = json.loads(req.content)['data']
        all_players += current
        index += 1

        # If no more players are returned through the URL, break        
        if len(current) == 0:
            break

    filter_pp(all_players)
    for i in players:
        if i.strip() in pp_map.keys():
            player = pp_map[i.strip()]
            bum_list.append(player)

    with open('bum_list', 'wb') as f:
        pickle.dump(bum_list, f)
        print('Wrote to bum_list')

    bum_list = rotogrinders(bum_list)

    bum_list = get_pp_toi(bum_list)
    display_bums(bum_list)

    # players = rotogrinders(players)
    # players = get_pp_toi(players)
    # display_bums(players)


    # display_bums(players)
    # for i in players:
    #     print(i)

    return bum_list

# if __name__ == '__main__':
#     pickle_open = open('bum_list', 'rb')
#     players = pickle.load(pickle_open)
#     get_bum_list(players)