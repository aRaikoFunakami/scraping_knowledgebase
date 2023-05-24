import re
import json
import sys
import logging
import csv

from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
#webdriver-manager for automatic updates of webdriver
from webdriver_manager.chrome import ChromeDriverManager


# debug config
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s")

# load config
args = sys.argv
CONFIG_FILE=args[1]

with open(CONFIG_FILE, 'r') as file:
    login = json.load(file)

USER = login['user']
PASS = login['password']
URL = login['url']
CHROME_DRIVER = login['chrome_driver']
TICKET_ID_BEGIN = int(login['ticket_id_begin'])
TICKET_ID_END = int(login['ticket_id_end'])

## Web Driver
# browser = webdriver.Chrome(CHROME_DRIVER)
## Web Driver from WebDriverManager
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.implicitly_wait(5)
    
def webdriver_login_acsmine(driver, user, password, url):
    # login to acs_mine
    driver.get( URL)
    browser.implicitly_wait(5)  
    # input username and password
    e = driver.find_element(By.ID, "username")
    e.clear()
    e.send_keys(USER)
    e = driver.find_element(By.ID, "password")
    e.clear()
    e.send_keys(PASS)
    # push submit button
    e = driver.find_element(By.ID, "login-submit")
    e.submit()
    return driver


# login acsmine server
browser = webdriver_login_acsmine(driver=browser, user=USER, password=PASS, url=URL)
browser.implicitly_wait(5)
    
# special URL for acs-knowledgebase articles
BASE_URL='https://gate.tok.access-company.com/redmine/projects/acs-knowledgebase/knowledgebase/articles/'

# load articles and write down them to a csv file
with open('./knowledge_db.csv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    # title line
    writer.writerow(['subject', 'description', 'source'])
    # articles
    for i in range(TICKET_ID_BEGIN, TICKET_ID_END, 1):
        # URL of knowledge-db articles
        url = BASE_URL + str(i)
        logging.info(url)
        browser.get(url)
        browser.implicitly_wait(5)
        # Skip page if 404 Error 
        error404 = browser.find_element(By.ID, "content").get_attribute("textContent")
        if '404' in error404:
            logging.info(error404)
            continue
        # Save contents (Subject + Article)
        subject = browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[3]/div[2]/div[2]").get_attribute("textContent")
        article = browser.find_element(By.ID, "article").get_attribute("textContent")
        # Delete unwanted whitespaces for LangChain API
        subject = re.sub(r'[ \t]+', ' ', subject)
        article = re.sub(r'[ \t]+', ' ', article)
        subject = re.sub(r'\n{3,}', '\n\n', subject)
        article = re.sub(r'\n{3,}', '\n\n', article)
        logging.info(subject + article)
        # save to the file
        writer.writerow([subject, article, url])

browser.quit()
