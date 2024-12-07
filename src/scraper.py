import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import requests
import sys
from datetime import date
from bs4 import BeautifulSoup
import time
from bum_list import get_bum_list
from subprocess import STDOUT, Popen, PIPE
                                                        # Replace date with current year
# https://www.nhl.com/stats/skaters?reportType=season&seasonFrom=2022&seasonTo=2022&gameType=2&filter=gamesPlayed,gte,1&sort=ppPoints&page=6&pageSize=100


######################################
# Update this every season; used in get_rosters()
CURRENT_SEASON = '20242025'
#
###################################
sys.path.append('.')
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
chrome_options.add_argument("--profile-directory=Default")
# Init chrome driver
PATH = "C:\Program Files\ChromeDriver\chromedriver.exe"
# driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
driver = []

not_on_pp_unit = []
all_betable_players = []

def dailyfaceoff(team_a, team_b, a_players, b_players):
    # Access denied without valid user-agent
    headers = { 'User-Agent': UserAgent().random }
    
    pp_links = []

    req = requests.get('https://www.dailyfaceoff.com/teams/', headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    team_links = soup.find_all(href=True)

    # Get the URLs for each teams powerplay roster
    for l in team_links:
        if team_a + '/line-combinations#powerplay' in l['href']:
            pp_links.append(l['href'])
        elif team_b + '/line-combinations#powerplay' in l['href']:
            pp_links.append(l['href'])  

    df_pp_units = pp_links

    # https://www.dailyfaceoff.com/
    for i in range(0, 2):
        # print('https://www.dailyfaceoff.com' + df_pp_units[i])
        try:
            req = requests.get('https://www.dailyfaceoff.com' + df_pp_units[i], headers=headers)
        except IndexError as e:
            print('Index Error')
            continue
        
        soup = BeautifulSoup(req.text, 'html.parser')

        data = soup.find_all('div', 'w-1/3')

        for i in data:
            if len(i['class']) == 1:
                df_pp_units.append(i.find('span', 'text-xs').text)
      
        # df_pp_units.append(soup.find('td', id='PPLW1').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPC1').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPRW1').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPLD1').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPRD1').find('a').text.strip())
        
        # df_pp_units.append(soup.find('td', id='PPLW2').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPC2').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPRW2').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPLD2').find('a').text.strip())
        # df_pp_units.append(soup.find('td', id='PPRD2').find('a').text.strip())

    pp_links = []

    # print("Hello")
    # req = requests.get('https://www.rotowire.com/hockey/nhl-lineups.php', headers=headers)
    # soup = BeautifulSoup(req.text, 'html.parser')
    # team_links = soup.find_all(href=True)

    for p in a_players:
        if p not in df_pp_units:
            print(p + ' is not on a powerplay unit: ' + team_a)
            not_on_pp_unit.append(p + ': ' + team_a)
    
    for p in b_players:
        if p not in df_pp_units:
            print(p + ' is not on a powerplay unit: ' + team_b)
            not_on_pp_unit.append(p + ': ' + team_b)

    return   

def get_team_abbrev(team):
    team_list = {
        'bruins': 'BOS',
        'sabres': 'BUF',
        'redwings': 'DET',
        'panthers': 'FLA',
        'canadiens': 'MTL',
        'senators': 'OTT',
        'lightning': 'TBL',
        'mapleleafs': 'TOR',
        'hurricanes': 'CAR',
        'bluejackets': 'CBJ',
        'devils': 'NJD',
        'islanders': 'NYI',
        'rangers': 'NYR',
        'flyers': 'PHI',
        'penguins': 'PIT',
        'capitals': 'WSH',
        'coyotes': 'ARI',
        'blackhawks': 'CHI',
        'avalanche': 'COL',
        'stars': 'DAL',
        'wild': 'MIN',
        'predators': 'NSH',
        'blues': 'STL',
        'jets': 'WPG',
        'ducks': 'ANA',
        'flames': 'CGY',
        'oilers': 'EDM',
        'kings': 'LAK',
        'sharks': 'SJS',
        'canucks': 'VAN',
        'goldenknights': 'VGK',
        'kraken': 'SEA'
    }

    return team_list[team]

def get_rosters(team_a, team_b, powerplayers):
    a_roster = []
    b_roster = []
    
    original_team_a = team_a
    original_team_b = team_b
    
    team_a = team_a.replace('-', '')
    team_b = team_b.replace('-', '')

    urls = [
        f'https://api-web.nhle.com/v1/roster/{get_team_abbrev(team_a)}/{CURRENT_SEASON}',
        f'https://api-web.nhle.com/v1/roster/{get_team_abbrev(team_b)}/{CURRENT_SEASON}'
    ]

    for k in range(0, 2):

        req = requests.get(urls[k])
        data = req.json()

        for i in data['forwards']:
            player = f'{i["firstName"]["default"]} {i["lastName"]["default"]}'
            a_roster.append(player) if k == 0 else b_roster.append(player)
        
        for i in data['defensemen']:
            player = f'{i["firstName"]["default"]} {i["lastName"]["default"]}'
            a_roster.append(player) if k == 0 else b_roster.append(player)

    a_team_bets = []
    b_team_bets = []

    for i in powerplayers:
        if i.strip() in a_roster:
            a_team_bets.append(i)
        elif i.strip() in b_roster:
            b_team_bets.append(i)

        all_betable_players.append(i.strip())

    # get_pp_unit(team_a, team_b, a_team_bets, b_team_bets)


    dailyfaceoff(original_team_a, original_team_b, a_team_bets, b_team_bets)
    
    
    # print('starting')
    # rotogrinders(team_a, team_b, a_team_bets, b_team_bets)
    return

def wait_till_reload(element, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.CLASS_NAME, element))
        )
    except:
        driver.execute_script('location.reload()')
        wait_till_reload(element, time)

def wait_for_ppp(time=2):
    if driver.find_element(By.CLASS_NAME, 'bbm-ShowMore'):
        return

    if (time > 5):
        print("Waiting too long")
        return

    driver.execute_script('location.reload()')
    time.sleep(time)
    wait_for_ppp(time +1)

# def get_pp_bets(game):
def get_pp_bets(teams_text, powerplayers):
    # game.click()
    # time.sleep(2)
    # driver.execute_script('location.reload()')
    
    # time.sleep(2)

    # #driver.find_element(By.CLASS_NAME, 'sph-MarketGroupNavBarButtonNew').click()
    # driver.get(driver.current_url + 'I6/O3') # I6 for player tab, I99 for same game parlay tab; /O3 opens all tabs

    # time.sleep(2)
    # # wait_till_reload('gl-MarketGroup', 5)
    
    # # all_sgp = driver.find_elements(By.CLASS_NAME, 'gl-MarketGroup')
    # all_sgp = driver.find_elements(By.CLASS_NAME, 'gl-MarketGroup')
    # powerplay_players = None

    # found_ppp = False
    # for b in all_sgp:
    #     if 'Player Powerplay Points' in b.get_attribute('innerText'):
    #         powerplay_players = b
    #         found_ppp = True

    # if not found_ppp:
    #     print("Power Play Not Found")
    #     return

    # powerplay_players = powerplay_players.find_elements(By.CLASS_NAME, 'srb-ParticipantLabelWithTeam_Name ')
    # powerplayers = []
    # for i in powerplay_players:
    #     powerplayers.append(i.get_attribute('innerHTML'))

    # teams_text = driver.find_element(By.CLASS_NAME, 'sph-EventHeader_Label')

    teams = teams_text.split('@')

    try:
        team_a = teams[0].strip().split(' ')
        team_b = teams[1].strip().split(' ')
    except:
        print("Stats Not Available")
        return  # Either too early for the stats, or the game is on

    # Extracts the names of each team into team_a and team_b
    # The if statements handle whether a team has two words in the end like Maple Leafs, or Golden Knights 

    if len(team_a) >= 3:
        team_a = team_a[1] + '-' + team_a[2]
    else:
        team_a = team_a[1]

    if len(team_b) >= 3:
        team_b = team_b[1] + '-' + team_b[2]
    else:
        team_b = team_b[1]

    get_rosters(team_a.lower(), team_b.lower(), powerplayers)
    return

# Deprecated; No longer works
# def get_daily_games():
#     driver.get('https://www.on.bet365.ca/#/AS/B17/')
    
#     try:
#         WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.CLASS_NAME, 'ff-FeaturedFixtureScroller'))
#         )
#     except:
#         print('error before')
    
#     game_list = len(driver.find_elements(By.CLASS_NAME, 'ffi-MarketIceHockeyFixtureDetails'))
#     count = 0

#     game_start_count = 0
#     print("Game Count: " + str(game_list))
#     for i in range(game_start_count, game_list):
#         driver.get('https://www.on.bet365.ca/#/AS/B17/')

#         wait_till_reload('ff-FeaturedFixtureScroller', 2)

#         games = driver.find_elements(By.CLASS_NAME, 'ffi-MarketIceHockeyFixtureDetails')
#         if 'Today' not in games[i].get_attribute('innerHTML'):
#             continue

#         get_pp_bets(games[i])
#         # time.sleep(2)
#         print(str(i + 1) + ' done')

#     print(not_on_pp_unit)
#     return

if __name__ == "__main__":
    # time.sleep((60 * 60)*8+(60*20))
    # Generates games.pickle file containing all needed information
    output = Popen(['python', 'src/daily_scrape.py'], stdout=PIPE, stderr = STDOUT)
    # output.wait()
    time.sleep(10)
    print('DONE')

    pickle_open = open('lib/games.pickle', 'rb')
    games = pickle.load(pickle_open)
    
    # games is an array with each item being an array aswell pertaing to a NHL game
    # The 0th index is always the two teams playing in that game while the rest of the array holds the players
    for g in games:
        team_text = g.pop(0)
        get_pp_bets(teams_text=team_text, powerplayers=g)

    # all_betable_players is just a list of player names
    get_bum_list(all_betable_players)
    
    print('http://localhost:3000')
    node = Popen(['node', '.'], stdout=PIPE, stderr = STDOUT)
    node.wait()
    exit(0)