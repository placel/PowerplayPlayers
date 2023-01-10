from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import requests
import pyautogui
import sys
from datetime import date
from bs4 import BeautifulSoup
import time
from bum_list import get_bum_list
                                                        # Replace date with current year
# https://www.nhl.com/stats/skaters?reportType=season&seasonFrom=2022&seasonTo=2022&gameType=2&filter=gamesPlayed,gte,1&sort=ppPoints&page=6&pageSize=100

sys.path.append('.')
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--profile-directory=Default")
# Init chrome driver
PATH = "C:\Program Files\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH, chrome_options=chrome_options)

not_on_pp_unit = []
all_betable_players = []

def rotogrinders(team_a, team_b, a_players, b_players):
    headers = { 'User-Agent': UserAgent().random }
    
    pp_links = []

    req = requests.get('https://rotogrinders.com/lineups/nhl?site=draftkings', headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    all_players = soup.find_all('span', 'pname')

    pp_players = []
    for i in range(0, len(a_players)):
        last_name = a_players[i].split(' ')[1]
        abbrevName = a_players[i].text[0] + ' ' + last_name
        if abbrevName in all_players:
            # Add code to check if the player is on a PPU, and if they are, append their name and which unit their on to an array
            if all_players[i].includes("PP1"):
                pp_players.append({a_players: {'ppUnit': 'PP1'}})
            elif all_players[i].includes("PP2"):
                pp_players.append({a_players: {'ppUnit': 'PP2'}})

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
        req = requests.get('https://www.dailyfaceoff.com' + df_pp_units[i], headers=headers)
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

def get_pp_unit(team_a, team_b, a_players, b_players):
    dailyfaceoff(team_a, team_b, a_players, b_players)
    return
    

def get_rosters(team_a, team_b, powerplayers):
    a_roster = []
    b_roster = []

    urls= ['https://www.nhl.com/' + team_a.replace('-', '') + '/roster/' + str(date.today().strftime('%y')), 
         'https://www.nhl.com/' + team_b.replace('-', '') + '/roster/' + str(date.today().strftime('%y'))]

    for k in range(0, 2):
        req = requests.get(urls[k])
        soup = BeautifulSoup(req.text, 'html.parser')

        offence = soup.find('table', class_='data-table__forwards')
        defence = soup.find('table', class_='data-table__defensemen')

        offence_first = offence.find_all('span', class_='name-col__firstName')
        offence_last = offence.find_all('span', class_='name-col__lastName')
        
        defence_first = defence.find_all('span', class_='name-col__firstName')
        defence_last = defence.find_all('span', class_='name-col__lastName')

        # print("-------")
        for i in range(0, len(offence_first)):
            first = offence_first[i].text
            last = offence_last[i].text
            fullname = first + ' ' + last
            if k == 0:
                a_roster.append(fullname)
            else:
                b_roster.append(fullname)

        for i in range(0, len(defence_first)):
            first = defence_first[i].text
            last = defence_last[i].text
            fullname = first + ' ' + last
            if k == 0:
                a_roster.append(fullname)
            else:
                b_roster.append(fullname)

    a_team_bets = []
    b_team_bets = []
    for i in powerplayers:
        # print(i)
        if i.strip() in a_roster:
            a_team_bets.append(i)
        elif i.strip() in b_roster:
            b_team_bets.append(i)

        all_betable_players.append(i.strip())

    # get_pp_unit(team_a, team_b, a_team_bets, b_team_bets)
    dailyfaceoff(team_a, team_b, a_team_bets, b_team_bets)
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

def get_pp_bets(game):
    game.click()
    time.sleep(2)
    driver.execute_script('location.reload()')
    
    time.sleep(2)

    #driver.find_element(By.CLASS_NAME, 'sph-MarketGroupNavBarButtonNew').click()
    driver.get(driver.current_url + 'I6/O3') # I6 for player tab, I99 for same game parlay tab; /O3 opens all tabs

    time.sleep(2)
    # wait_till_reload('gl-MarketGroup', 5)
    
    # all_sgp = driver.find_elements(By.CLASS_NAME, 'gl-MarketGroup')
    all_sgp = driver.find_elements(By.CLASS_NAME, 'gl-MarketGroup')
    powerplay_players = None

    found_ppp = False
    for b in all_sgp:
        if 'Player Powerplay Points' in b.get_attribute('innerText'):
            powerplay_players = b
            found_ppp = True

    if not found_ppp:
        print("Power Play Not Found")
        return

    powerplay_players = powerplay_players.find_elements(By.CLASS_NAME, 'srb-ParticipantLabelWithTeam_Name ')
    powerplayers = []
    for i in powerplay_players:
        powerplayers.append(i.get_attribute('innerHTML'))

    teams_text = driver.find_element(By.CLASS_NAME, 'sph-EventHeader_Label')
    teams = teams_text.find_element(By.TAG_NAME, 'span').get_attribute('innerHTML').split('@')

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

def get_daily_games():
    driver.get('https://www.on.bet365.ca/#/AS/B17/')

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ff-FeaturedFixtureScroller'))
        )
    except:
        print('error before')
    
    game_list = len(driver.find_elements(By.CLASS_NAME, 'ffi-MarketIceHockeyFixtureDetails'))
    count = 0

    print("Game Count: " + str(game_list))
    for i in range(0, game_list):
        driver.get('https://www.on.bet365.ca/#/AS/B17/')

        wait_till_reload('ff-FeaturedFixtureScroller', 2)

        games = driver.find_elements(By.CLASS_NAME, 'ffi-MarketIceHockeyFixtureDetails')
        if 'Today' not in games[i].get_attribute('innerHTML'):
            continue

        get_pp_bets(games[i])
        # time.sleep(2)
        print(str(i + 1) + ' done')

    print(not_on_pp_unit)
    return

if __name__ == "__main__":
    get_daily_games()
    print('Done.')
    get_bum_list(all_betable_players)
    driver.close()
    exit(0)