from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import pyautogui
import time

username = 'FormerFatty'
password = 'Gronk612'

chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--profile-directory=Default")
# Init chrome driver
PATH = "C:\Program Files\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH, chrome_options=chrome_options)

driver.get('https://www.on.bet365.ca/#/AS/B17/')

pyautogui.press("f12")
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'ff-FeaturedFixtureScroller'))
)


driver.find_element(By.CLASS_NAME, 'hm-MainHeaderRHSLoggedOutNarrow_Login').click()
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'lms-StandardLogin_Username'))
)

time.sleep(1)
driver.find_element(By.CLASS_NAME, 'lms-StandardLogin_Username ').click()
script = f'document.querySelector("body > div.lms-LoginModule > div > div.lms-StandardLogin_Container > div > div:nth-child(2) > input").value = "{username}"'
driver.execute_script(script)

driver.find_element(By.CLASS_NAME, 'lms-StandardLogin_Password ').click()

script = f'document.querySelector("body > div.lms-LoginModule > div > div.lms-StandardLogin_Container > div > div:nth-child(3) > input").value = "hi"'
driver.execute_script(script)

driver.find_element(By.CLASS_NAME, 'lms-LoginButton ').click()
time.sleep(10)