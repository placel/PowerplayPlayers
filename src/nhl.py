from fake_useragent import UserAgent
import requests
from datetime import date, datetime
import json
import pandas
from bs4 import BeautifulSoup

CURRENT_SEASON = '20232024'

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

df = pandas.DataFrame(nhl_get_team_stats())
print(df)