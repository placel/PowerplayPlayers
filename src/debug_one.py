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

items = driver.execute_script('return Array.from(document.getElementsByClassName("sm-SplashMarket"))')
driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { if (arguments[0][i].innerHTML.includes(">Player<")) { arguments[0][i].click(); break; } }', items)

items = driver.execute_script('return Array.from(document.getElementsByClassName("sm-CouponLink"))')
driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { if (arguments[0][i].innerHTML.includes(">Player Powerplay Points<")) { arguments[0][i].click(); break; } }', items)

# used to send the URL to the host process py_testing.py
print(driver.current_url)