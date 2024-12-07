from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time


chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#Change chrome driver path accordingly
PATH = "C:\Program Files\ChromeDriver\chromedriver.exe"
service = Service(PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
print(driver.title)

# items = driver.execute_script('return Array.from(document.getElementsByClassName("src-FixtureSubGroup_Closed"))')
# driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { arguments[0][i].click() }', items)

# Open all game tabs to reveal all players
# driver.execute_script("""
#     let x = Array.from(document.getElementsByClassName("src-HScrollFixtureSubGroupWithBottomBorder_Closed"))

#     x.forEach(element => {
#         element.click();
#     });
# """)

# players = driver.execute_script('return ""')
# items = driver.execute_script('return Array.from(document.getElementsByClassName("srb-ParticipantLabelWithTeam_Name"))')
# players = driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { arguments[1] = arguments[1].toString().concat((arguments[0][i].innerText.toString().concat("|"))); }; console.log(arguments[1]); return arguments[1];', items, players)

driver.execute_script("""
    let y = Array.from(document.getElementsByClassName("src-HScrollFixtureSubGroupWithBottomBorder_Closed"))

    y.forEach(element => {
        element.click();
    });
""")

time.sleep(2)

script = """

let x = Array.from(document.getElementsByClassName("gl-MarketGroupPod"));
let result = "";

for (let i = 0; i < x.length; i++) {
    // Get the game description (team names)
    let gameDescription = x[i].getElementsByClassName("src-FixtureSubGroupButton_Text")[0].innerText;

    // Add the game description to the result
    result += gameDescription + "|";

    // Get player names for each team
    let players = Array.from(x[i].getElementsByClassName("srb-ParticipantLabelWithTeam_Name"));
    
    // Add player names to the result
    for (let j = 0; j < players.length; j++) {
        result += players[j].innerText + "|";
    }

    // Get the time the game starts
    // let gameTime = x[i].getElementsByClassName("src-FixtureSubGroupButton_BookCloses")[0].innerText;

    // Add the game time to the result
    // result += gameTime + "|";

    // Optionally, you could collect the odds for each team (from the "srb-HScrollOddsMarket" elements)
    // let odds = Array.from(x[i].getElementsByClassName("gl-ParticipantOddsOnly"));
    
    // for (let k = 0; k < odds.length; k++) {
    //    result += odds[k].getElementsByClassName("gl-ParticipantOddsOnly_Odds")[0].innerText + "|";
    // }
}

return result;
"""

result = driver.execute_script(script)
# games = driver.execute_script('return Array.from(document.getElementsByClassName("src-FixtureSubGroup "))')
# games = driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { console.log(arguments[0][i].getElementsByClassName("srb-ParticipantLabelWithTeam_Name ")) };', games)

# print(result)
# result = "".join(players)
print("EX" + str(result))

print(driver.current_url)

player_clicks = []

# for i in items:
#     # print(i.find('span', 'sm-CouponLink_Title '))
#     print(i.get_property('attributes'))
#     print('-----')
# print('Length' + str(len(tabs)))

# for i in tabs:
#     if 'Player' in i.get_attribute('innerHTML'):
#         player_clicks.append(i)
#         print('Found')