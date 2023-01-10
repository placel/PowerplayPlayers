from fake_useragent import UserAgent
import requests
from datetime import date
import json
import pickle
import pandas

PPP_LIMIT = 4
pp_map = dict()

def filter_pp(players):
    for p in players:
        if p['ppPoints'] <= PPP_LIMIT:
            pp_map[p['skaterFullName']] = {'skaterFullName': {
                    'assists': p['assists'],
                    'gamesPlayed': p['gamesPlayed'],
                    'plusMinus': p['plusMinus'],
                    'points': p['points'],
                    'pointsPerGame': p['pointsPerGame'],
                    'ppGoals': p['ppGoals'],
                    'ppPoints': p['ppPoints'],
                    'teamAbbrevs': p['teamAbbrevs'],
                    'timeOnIcePerGame': p['timeOnIcePerGame']
                }}

def display_bums(players):
    df = pandas.DataFrame(players)
    
    print(df.head())

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
            print("<---------------->")
            print('  ' + i + ': ' + player['skaterFullName']['teamAbbrevs'])
            print('  PP: ' + str(player['skaterFullName']['ppPoints']))
            bum_list.append(player)

    with open('bum_list', 'wb') as f:
        pickle.dump(bum_list, f)

    # display_bums(players)
    # for i in players:
    #     print(i)

    return bum_list

# if __name__ == '__main__':
#     pickle_open = open('bum_list', 'rb')
#     players = pickle.load(pickle_open)
    
#     get_bum_list(players)