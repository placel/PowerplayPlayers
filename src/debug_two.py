from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print('Hello')

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#Change chrome driver path accordingly
PATH = "C:\Program Files\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
print(driver.title)

# Open all game tabs to reveal all players
items = driver.execute_script('return Array.from(document.getElementsByClassName("src-FixtureSubGroup_Closed"))')
driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { arguments[0][i].click() }', items)

# players = driver.execute_script('return ""')
# items = driver.execute_script('return Array.from(document.getElementsByClassName("srb-ParticipantLabelWithTeam_Name"))')
# players = driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { arguments[1] = arguments[1].toString().concat((arguments[0][i].innerText.toString().concat("|"))); }; console.log(arguments[1]); return arguments[1];', items, players)


script = """
console.log('hi');
let x = Array.from(document.getElementsByClassName("src-FixtureSubGroup "));
let result = "";

for (let i = 0; i < x.length; i++) {
  console.log(x[i]);
  let game = Array.from(x[i].getElementsByClassName("srb-ParticipantLabelWithTeam_Name "));
             
  result += x[i].getElementsByClassName("src-FixtureSubGroupButton_Text ")[0].innerText + "|";

  for (let k = 0; k < game.length; k++) {
    result += game[k].innerText + "|"
  }
  
  console.log(x[i].getElementsByClassName("src-FixtureSubGroupButton_Text ")[0].innerText)
  
}

return result;"""

result = driver.execute_script(script)
# games = driver.execute_script('return Array.from(document.getElementsByClassName("src-FixtureSubGroup "))')
# games = driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { console.log(arguments[0][i].getElementsByClassName("srb-ParticipantLabelWithTeam_Name ")) };', games)



# games = "".join(result)

print("EX" + str(result))

print(driver.current_url)
print("hello")

player_clicks = []

# for i in items:
#     # print(i.find('span', 'sm-CouponLink_Title '))
#     print(i.get_property('attributes'))
#     print('-----')
print('Running')
# print('Length' + str(len(tabs)))

# for i in tabs:
#     if 'Player' in i.get_attribute('innerHTML'):
#         player_clicks.append(i)
#         print('Found')