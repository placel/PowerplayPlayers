#########################################################
#
#   THIS SCRIPT SCRAPES THE LAST NIGHTS NHL GAMES
#   AND UPDATES THE DATABASE WITH THE NEW DATA
#   
#   SCRIPT SHOULD BE RUN DAILY
#
#########################################################


from datetime import datetime, timedelta
from fake_useragent import UserAgent
import pandas as pd
import requests
import time
import json

CURRENT_SEASON: str = '20232024'
TOTAL_REQUESTS = 0

def total_requests():
    global TOTAL_REQUESTS
    TOTAL_REQUESTS = TOTAL_REQUESTS + 1

def load_csv(filename='.\src\AI\data\database\player-database.csv'):
    df = pd.read_csv(filename, index_col=False)
    return df

def update_csv(df, filename):    
    df.to_csv(filename, index=False)
    return 

def get_player_summary_report(headers, date_to_scrape):
    url = f'https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=true&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22goals%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22assists%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22playerId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=1000&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameDate%3C=%22{date_to_scrape}%2023%3A59%3A59%22%20and%20gameDate%3E=%22{date_to_scrape}%22%20and%20gameTypeId=2'
    req = requests.get(url, headers=headers)

    total_requests()
    return_count = json.loads(req.content)['total']

    # If there are no players that played on the date_to_scrape, return an empty list
    if return_count <= 0:
        return []
    
    # If there are more than 50 players that played on the date_to_scrape, we need to make multiple requests to get all the players
    request_count = (return_count // 50) + 1 

    # Realllly dumb to make the same request twice, but I'm too lazy to fix it (Inital request is to get the total number of players, second is to get the actual data)
    player_collection = []
    for i in range(request_count):
        url = f'https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=true&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22goals%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22assists%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22playerId%22,%22direction%22:%22ASC%22%7D%5D&start={(i * 50)}&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameDate%3C=%22{date_to_scrape}%2023%3A59%3A59%22%20and%20gameDate%3E=%22{date_to_scrape}%22%20and%20gameTypeId=2'
        req = requests.get(url, headers=headers)
        total_requests()
        player_collection += json.loads(req.content)['data']
    
    return player_collection

def get_player_powerplay_report(headers, date_to_scrape):
    url = f'https://api.nhle.com/stats/rest/en/skater/powerplay?isAggregate=false&isGame=true&sort=%5B%7B%22property%22%3A%22ppTimeOnIce%22%2C%22direction%22%3A%22DESC%22%7D%2C%7B%22property%22%3A%22playerId%22%2C%22direction%22%3A%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E%3D1&cayenneExp=gameDate%3C%3D%22{date_to_scrape}+23%3A59%3A59%22+and+gameDate%3E%3D%22{date_to_scrape}%22+and+gameTypeId%3D2'
    req = requests.get(url, headers=headers)

    total_requests()
    return_count = json.loads(req.content)['total']

    # If there are no players that played on the date_to_scrape, return an empty list
    if return_count == 0:
        return []
    
    # If there are more than 50 players that played on the date_to_scrape, we need to make multiple requests to get all the players
    request_count = (return_count // 50) + 1

    # Realllly dumb to make the same request twice, but I'm too lazy to fix it (Inital request is to get the total number of players, second is to get the actual data)
    player_collection = []
    for i in range(request_count):
        url = f'https://api.nhle.com/stats/rest/en/skater/powerplay?isAggregate=false&isGame=true&sort=%5B%7B%22property%22%3A%22ppTimeOnIce%22%2C%22direction%22%3A%22DESC%22%7D%2C%7B%22property%22%3A%22playerId%22%2C%22direction%22%3A%22ASC%22%7D%5D&start={(i * 50)}&limit=50&factCayenneExp=gamesPlayed%3E%3D1&cayenneExp=gameDate%3C%3D%22{date_to_scrape}+23%3A59%3A59%22+and+gameDate%3E%3D%22{date_to_scrape}%22+and+gameTypeId%3D2'
        req = requests.get(url, headers=headers)
        total_requests()
        player_collection += json.loads(req.content)['data']

    return player_collection

def get_team_summary_report(headers, date_to_scrape):
    url = f'https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=true&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22wins%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameDate%3C=%22{date_to_scrape}%2023%3A59%3A59%22%20and%20gameDate%3E=%22{date_to_scrape}%22%20and%20gameTypeId=2'
    req = requests.get(url, headers=headers)

    total_requests()
    team_collection = json.loads(req.content)['data']

    # If there are no players that played on the date_to_scrape, return an empty list
    if team_collection.count == 0:
        return []
    
    return team_collection

def get_team_powerplay_report(headers, date_to_scrape):
    url = f'https://api.nhle.com/stats/rest/en/team/powerplay?isAggregate=false&isGame=true&sort=%5B%7B%22property%22:%22powerPlayPct%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameDate%3C=%22{date_to_scrape}%2023%3A59%3A59%22%20and%20gameDate%3E=%22{date_to_scrape}%22%20and%20gameTypeId=2'
    req = requests.get(url, headers=headers)

    total_requests()
    team_collection = json.loads(req.content)['data']

    # If there are no players that played on the date_to_scrape, return an empty list
    if team_collection.count == 0:
        return []
    
    return team_collection

def get_team_penalty_report(headers, date_to_scrape):
    url = f'https://api.nhle.com/stats/rest/en/team/penalties?isAggregate=false&isGame=true&sort=%5B%7B%22property%22:%22penaltyMinutes%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameDate%3C=%22{date_to_scrape}%2023%3A59%3A59%22%20and%20gameDate%3E=%22{date_to_scrape}%22%20and%20gameTypeId=2'
    req = requests.get(url, headers=headers)

    total_requests()
    team_collection = json.loads(req.content)['data']

    # If there are no players that played on the date_to_scrape, return an empty list
    if team_collection.count == 0:
        return []
    
    return team_collection

def get_team_penalty_kill_report(headers, date_to_scrape):
    url = f'https://api.nhle.com/stats/rest/en/team/penaltykill?isAggregate=false&isGame=true&sort=%5B%7B%22property%22:%22penaltyKillPct%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22teamId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=50&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameDate%3C=%22{date_to_scrape}%2023%3A59%3A59%22%20and%20gameDate%3E=%22{date_to_scrape}%22%20and%20gameTypeId=2'
    req = requests.get(url, headers=headers)

    total_requests()
    team_collection = json.loads(req.content)['data']

    # If there are no players that played on the date_to_scrape, return an empty list
    if team_collection.count == 0:
        return []
    
    return team_collection

def collect_player_reports(headers, seasons_to_scrape):
    for i, season in enumerate(seasons_to_scrape):
        
        START_DATE = season[0]
        END_DATE = season[1]
        date_to_scrape = START_DATE

        while date_to_scrape <= END_DATE:
            # Collect the data
            player_summary_report = get_player_summary_report(headers=headers, date_to_scrape=date_to_scrape)
            player_powerplay_report = get_player_powerplay_report(headers=headers, date_to_scrape=date_to_scrape)

            if len(player_summary_report) == 0:
                date_to_scrape += timedelta(days=1)
                continue

            # Convert the data to a pandas dataframe
            psr_df = pd.DataFrame(player_summary_report)
            ppr_df = pd.DataFrame(player_powerplay_report)

            # Figure out which columns to keep
            cols_to_use = ppr_df.columns.difference(psr_df.columns)
            cols_to_use = cols_to_use.insert(0, 'playerId')

            # Merge the dataframes; only add unique columns from ppr_df (cols_to_use)
            df = pd.merge(psr_df, ppr_df[cols_to_use], on='playerId', how='right')

            # Load the current csv, append the new data, and update the csv
            csv_df = load_csv(filename=f'.\src\AI\data\database\player-database.csv')
            csv_df = pd.concat([csv_df, df])

            update_csv(df=csv_df, filename=f'.\src\AI\data\database\player-database.csv')
            print(f'date_to_scrape: {date_to_scrape}\n')

            # Increment the date_to_scrape by 1 day
            date_to_scrape += timedelta(days=1)
        
        print(f'{START_DATE.year}-{END_DATE.year} season complete...\n')

def collect_team_reports(headers, seasons_to_scrape):
    for i, season in enumerate(seasons_to_scrape):
        
        START_DATE = season[0]
        END_DATE = season[1]
        date_to_scrape = START_DATE

        while date_to_scrape <= END_DATE:
            # Collect the data
            team_summary_report = get_team_summary_report(headers=headers, date_to_scrape=date_to_scrape)
            team_powerplay_report = get_team_powerplay_report(headers=headers, date_to_scrape=date_to_scrape)
            team_penalty_report = get_team_penalty_report(headers=headers, date_to_scrape=date_to_scrape)
            team_penalty_kill_report = get_team_penalty_kill_report(headers=headers, date_to_scrape=date_to_scrape)

            # If there are no players that played on the date_to_scrape, skip, and increment the date_to_scrape by 1 day
            if len(team_summary_report) == 0:
                date_to_scrape += timedelta(days=1)
                continue

            # Convert the data to a pandas dataframe
            tsr_df = pd.DataFrame(team_summary_report)
            tpr_df = pd.DataFrame(team_powerplay_report)
            tpenr_df = pd.DataFrame(team_penalty_report)
            tpenk_df = pd.DataFrame(team_penalty_kill_report)
            
            # Figure out which columns to keep
            cols_to_use = tpr_df.columns.difference(tsr_df.columns)
            cols_to_use = cols_to_use.insert(0, 'teamId')

            # Merge the dataframes; only add unique columns from ppr_df (cols_to_use)
            df = pd.merge(tsr_df, tpr_df[cols_to_use], on='teamId', how='right')

            cols_to_use = tpenr_df.columns.difference(df.columns)
            cols_to_use = cols_to_use.insert(0, 'teamId')

            # Merge the dataframes; only add unique columns from ppr_df (cols_to_use)
            df = pd.merge(df, tpenr_df[cols_to_use], on='teamId', how='right')

            cols_to_use = tpenk_df.columns.difference(df.columns)
            cols_to_use = cols_to_use.insert(0, 'teamId')

            # Merge the dataframes; only add unique columns from ppr_df (cols_to_use)
            df = pd.merge(df, tpenk_df[cols_to_use], on='teamId', how='right')

            print(df.columns)
            # Load the current csv, append the new data, and update the csv
            csv_df = load_csv(filename=f'.\src\AI\data\database\\team-database.csv')
            csv_df = pd.concat([csv_df, df])

            update_csv(df=csv_df, filename=f'.\src\AI\data\database\\team-database.csv')
            print(f'date_to_scrape: {date_to_scrape}\n')

            # Increment the date_to_scrape by 1 day
            date_to_scrape += timedelta(days=1)
        
        print(f'{START_DATE.year}-{END_DATE.year} season complete...\n')

def collect_data():
    TODAY_DATE = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
    YESTERDAY_DATE = TODAY_DATE - timedelta(days=1)
    HEADERS = { 'User-Agent': UserAgent().random }

    # datetime formatted array of tuples
    # Each tuple is a season to scrape, 0th index being the start date, 1st index being the end
    SEASONS_TO_SCRAPE = [
        (datetime.strptime(f'{YESTERDAY_DATE}', '%Y-%m-%d').date(), datetime.strptime(f'{TODAY_DATE}', '%Y-%m-%d').date())
    ]

    collect_player_reports(headers=HEADERS, seasons_to_scrape=SEASONS_TO_SCRAPE)
    collect_team_reports(headers=HEADERS, seasons_to_scrape=SEASONS_TO_SCRAPE)

def data_processing():

    nhl_teams = {
        'Anaheim Ducks': 'ANA',
        'Arizona Coyotes': 'ARI',
        'Boston Bruins': 'BOS',
        'Buffalo Sabres': 'BUF',
        'Calgary Flames': 'CGY',
        'Carolina Hurricanes': 'CAR',
        'Chicago Blackhawks': 'CHI',
        'Colorado Avalanche': 'COL',
        'Columbus Blue Jackets': 'CBJ',
        'Dallas Stars': 'DAL',
        'Detroit Red Wings': 'DET',
        'Edmonton Oilers': 'EDM',
        'Florida Panthers': 'FLA',
        'Los Angeles Kings': 'LAK',
        'Minnesota Wild': 'MIN',
        'Montréal Canadiens': 'MTL',
        'Nashville Predators': 'NSH',
        'New Jersey Devils': 'NJD',
        'New York Islanders': 'NYI',
        'New York Rangers': 'NYR',
        'Ottawa Senators': 'OTT',
        'Philadelphia Flyers': 'PHI',
        'Pittsburgh Penguins': 'PIT',
        'San Jose Sharks': 'SJS',
        'Seattle Kraken': 'SEA',
        'St. Louis Blues': 'STL',
        'Tampa Bay Lightning': 'TBL',
        'Toronto Maple Leafs': 'TOR',
        'Vancouver Canucks': 'VAN',
        'Vegas Golden Knights': 'VGK',
        'Washington Capitals': 'WSH',
        'Winnipeg Jets': 'WPG'
    }

    team_df = pd.read_csv('.\src\AI\data\database\\team-database.csv')
    player_df = pd.read_csv('.\src\AI\data\database\player-database.csv')

    team_df['teamAbbrev'] = team_df['teamFullName'].map(nhl_teams)
    team_df = pd.merge(team_df, team_df, left_on=['teamAbbrev', 'gameId'], right_on=['opponentTeamAbbrev', 'gameId'], suffixes=('', '_opponent'))
    
    df = pd.merge(team_df, player_df, on=['teamAbbrev', 'gameId'])
    df = df.loc[:, ~df.columns.str.endswith('_x')]
    df = df.apply(lambda x: x.replace('_y', '') if x.name.endswith('_y') else x)

    for i in df.columns:
        if i.endswith('_y'):
            df.rename(columns={i: i.replace('_y', '')}, inplace=True)
    
    df = df.fillna(0)
    df = df.drop_duplicates()

    df.to_csv('.\src\AI\data\database\current-database.csv', index=False)

def main():
    start_time = datetime.now()
    collect_data()
    # data_processing()
    end_time = datetime.now()

    print(f'Total requests: {TOTAL_REQUESTS}')
    print(f'Time taken: {end_time - start_time}')

if __name__ == '__main__':
    main()