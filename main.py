from dotenv import load_dotenv
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
load_dotenv()

from re import match
from os import getenv, path
from time import sleep
from threading import Thread
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from flask import Flask, render_template, url_for
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pymongo import MongoClient
mongo = MongoClient('mongodb+srv://Henboy:21jPzi3zFEvClGnv@cluster0.rlxx6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db_counter = mongo.db.counter
find = db_counter.find_one({'deleted': {'$exists': True}})
if not find: db_counter.insert_one({'deleted': 0, 'since': datetime.now()})
find = db_counter.find_one({'deleted': {'$exists': True}})

app = Flask(__name__)
twitter_link = 'https://twitter.com/rendersbyian'

count, deleted, since, seconds = 0, find['deleted'], find['since'].strftime('%A, %B %d %Y'), 30
CHROMEDRIVER_PATH = fr'{getenv("CHROMEDRIVER_PATH")}/bin/chromedriver'

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.binary_location = getenv('GOOGLE_CHROME_BIN')
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
wait, first_time, tweets = WebDriverWait(driver, 10), True, 0


def background_updater():
    global first_time, tweets, deleted

    while True:
        if first_time:
            sleep(3)
            print('\nThe website is up ＼（＾○＾）／\n')
            first_time = False

        driver.get(twitter_link)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"] h2[role="heading"] + div[dir="auto"]')))
        check = driver.find_element_by_css_selector('[data-testid="primaryColumn"] h2[role="heading"] + div[dir="auto"]')
        number = int(match(r'[\d,]+', check.text).group().replace(',', ''))
        if number < tweets:
            deleted += (tweets - number)
            db_counter.find_one_and_update({'deleted': {'$exists': True}}, {'$set': {'deleted': deleted}}, upsert=True)

        tweets = number
        sleep(seconds)

Thread(target=background_updater).start()

@app.route('/')
def hello():
    return render_template('index.html', tweets=tweets, deleted=deleted, since=since)

PORT = getenv('PORT') or 8080
if __name__ == '__main__':
    app.run('0.0.0.0', int(PORT))
    driver.close()
