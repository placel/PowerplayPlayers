from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

print('Hello')

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#Change chrome driver path accordingly
PATH = "C:\Program Files\ChromeDriver\chromedriver.exe"
service = Service(PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
print(driver.title)

# deprecated in UI overhaul but keeping just in case
# items = driver.execute_script('return Array.from(document.getElementsByClassName("sm-SplashMarket"))')
# driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { if (arguments[0][i].innerHTML.includes(">Player<")) { arguments[0][i].click(); break; } }', items)

driver.execute_script('document.getElementsByClassName("lrl-ListRibbon_ViewAllLink ")[0]?.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));')
# time.sleep(20)
# items = driver.execute_script('return Array.from(document.getElementsByClassName("sm-CouponLink"))')
# driver.execute_script('for (let i = 0; i < arguments[0].length; i++) { if (arguments[0][i].innerHTML.includes(">Player Power Play Points<")) { arguments[0][i].click(); break; } }', items)

# used to send the URL to the host process py_testing.py
print(driver.current_url)