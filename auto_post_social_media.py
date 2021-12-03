import undetected_chromedriver.v2 as uc
import os
from pathlib import Path
from bs4 import BeautifulSoup
import lxml
import time
from random import uniform
from selenium.webdriver.common.keys import Keys
import traceback
import json
from pprint import pprint
from cleaner import Cleaner
from datetime import datetime


def get_driver(headless=True):
    if not (os.path.exists("./chrome_profile")):
        os.mkdir('./chrome_profile')
        Path('./chrome_profile/First Run').touch()
    options = uc.ChromeOptions()
    if headless:
        options.headless = True
    options.add_argument('--user-data-dir=./chrome_profile/')
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def pause():
    time.sleep(uniform(1, 2))


def enter_text(input, text):
    input.clear()
    for char in text:
        input.send_keys(char)
        time.sleep(uniform(0.1, 0.3))


def execute_function(function, *args):
    while True:
        try:
            if function.__name__ in ("log_in_to_facebook", "log_in_to_twitter", "log_in_to_linkedin"):
                function(args[0], args[1], args[2])
            elif function.__name__ in ("post_to_twitter", "post_to_facebook", "post_to_linkedin"):
                function(args[0], args[1])
            break
        except Exception:
            print(traceback.format_exc())


def wait_for_css_selector(driver, css_selector):
    while not BeautifulSoup(driver.page_source, 'lxml').select(css_selector):
        if driver.current_url in (
        "https://twitter.com/home", "https://www.facebook.com/", "https://www.linkedin.com/feed/"):
            return True
        print('wait_for_css_selector:', css_selector)
        time.sleep(1)


def wait_for_text(driver, text):
    while text not in BeautifulSoup(driver.page_source, 'lxml'):
        time.sleep(0.2)
    print("posting...")
    while text in BeautifulSoup(driver.page_source, 'lxml'):
        time.sleep(1)


def clean_text(text):
    return Cleaner().clean(BeautifulSoup(text, "lxml").text)


def log_in_to_facebook(driver, email, password):
    driver.get("https://www.facebook.com/")
    response = wait_for_css_selector(driver, "#email")
    if response:
        return
    if not driver.find_element_by_xpath('//form[@data-testid="royal_login_form"]'):
        return
    email_input = driver.find_element_by_id("email")
    enter_text(email_input, email)
    pause()
    password_input = driver.find_element_by_id("pass")
    enter_text(password_input, password)
    pause()
    password_input.send_keys(Keys.RETURN)
    time.sleep(100)


def log_in_to_twitter(driver, email, password):
    driver.get("https://twitter.com/login")
    email_css_selector = 'input[autocomplete="username"]'
    response = wait_for_css_selector(driver, email_css_selector)
    if response:
        return
    email_input = driver.find_element_by_css_selector(email_css_selector)
    enter_text(email_input, email)
    email_input.send_keys(Keys.RETURN)
    pause()
    password_css_selector = 'input[autocomplete="current-password"]'
    wait_for_css_selector(driver, password_css_selector)
    password_input = driver.find_element_by_css_selector(password_css_selector)
    enter_text(password_input, password)
    password_input.send_keys(Keys.RETURN)
    pause()
    time.sleep(100)


def log_in_to_linkedin(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    email_css_selector = '#username'
    response = wait_for_css_selector(driver, email_css_selector)
    if response:
        return
    email_input = driver.find_element_by_css_selector(email_css_selector)
    enter_text(email_input, email)
    pause()
    password_css_selector = '#password'
    wait_for_css_selector(driver, password_css_selector)
    password_input = driver.find_element_by_css_selector(password_css_selector)
    enter_text(password_input, password)
    password_input.send_keys(Keys.RETURN)
    pause()
    time.sleep(100)


def post_to_twitter(driver, dict):
    if driver.current_url != "https://twitter.com/home":
        driver.get("https://twitter.com/home")
    tweet_input_css_selector = '[aria-label="Tweet text"]'
    wait_for_css_selector(driver, tweet_input_css_selector)
    pause()
    tweet_input = driver.find_element_by_css_selector(tweet_input_css_selector)
    tweet_input.send_keys(f"{dict['custom_text']}\n{dict['start_time']}\n{dict['event_name']}\n{dict['purchase_link']}")
    pause()
    driver.find_element_by_css_selector('div[data-testid="tweetButtonInline"]').click()
    time.sleep(60)


def post_to_facebook(driver, dict):
    if driver.current_url != "https://www.facebook.com/":
        driver.get("https://www.facebook.com/")
    post_input_css_selector = 'div[aria-label="Create a post"] div[role="button"]'
    wait_for_css_selector(driver, post_input_css_selector)
    driver.find_element_by_css_selector(post_input_css_selector).click()
    post_input_css_selector = 'div[role="presentation"] div[role="textbox"]'
    wait_for_css_selector(driver, post_input_css_selector)
    pause()
    post_input = driver.find_element_by_css_selector(post_input_css_selector)
    post_input.send_keys(f"{dict['custom_text']}\n{dict['start_time']}\n{dict['event_name']}\n{dict['speaker']}"
                         f"\n\n{dict['purchase_link']}\n\n{dict['description']}")
    pause()
    driver.find_element_by_css_selector('div[aria-label="Post"]').click()
    time.sleep(60)


def post_to_linkedin(driver, dict):
    if driver.current_url != "https://www.linkedin.com/feed/":
        driver.get("https://www.linkedin.com/feed/")
    post_input_css_selector = 'div[class^="share-box-feed-entry__"] div[class^="display-flex "] button'
    wait_for_css_selector(driver, post_input_css_selector)
    driver.find_element_by_css_selector(post_input_css_selector).click()
    post_input_css_selector = 'div[class^="ql-editor "][role="textbox"]'
    wait_for_css_selector(driver, post_input_css_selector)
    pause()
    post_input = driver.find_element_by_css_selector(post_input_css_selector)
    post_input.send_keys(f"{dict['custom_text']}\n{dict['start_time']}\n{dict['event_name']}\n{dict['speaker']}"
                         f"\n\n{dict['purchase_link']}\n\n{dict['description']}")
    pause()
    driver.find_element_by_css_selector('button[class^="share-actions__primary-action"]').click()
    time.sleep(60)


def main():
    driver = get_driver(headless=False)
    facebook_email = "email@gmail.com"
    facebook_password = "password"
    twitter_email = "email@gmail.com"
    twitter_password = "password"
    linkedin_email = "email@gmail.com"
    linkedin_password = "password"
    with open('json_text.json') as j_f:
        json_test = json.load(j_f)
        for event in json_test:
            if event['eventType'] in ("Simulive Replay", "Webinar"):
                facebook_linkedin_dict = {
                    "custom_text": "custom text",
                    "start_time": datetime.strptime("2021-11-03T17:00:00Z", "%Y-%m-%dT%H:%M:%SZ").strftime('%B %d, %Y %I:%M %p'),
                    "event_name": clean_text(event['eventName'].replace('\n', '. ')),
                    "speaker": "Presented by {}".format(clean_text(event['speakers'][0]['name']).replace('\n', '. ')),
                    "purchase_link": event["purchasePageLink"],
                    "description": clean_text(event["description"])
                }
                execute_function(log_in_to_linkedin, driver, linkedin_email, linkedin_password)
                execute_function(post_to_linkedin, driver, facebook_linkedin_dict)
                execute_function(log_in_to_facebook, driver, facebook_email, facebook_password)
                execute_function(post_to_facebook, driver, facebook_linkedin_dict)
                twitter_dict = {
                    "custom_text": "custom text",
                    "start_time": datetime.strptime("2021-11-03T17:00:00Z", "%Y-%m-%dT%H:%M:%SZ").strftime('%B %d, %Y %I:%M %p'),
                    "event_name": clean_text(event['eventName'].replace('\n', '. ')),
                    "purchase_link": event["purchasePageLink"]
                }
                execute_function(log_in_to_twitter, driver, facebook_email, facebook_password)
                execute_function(post_to_twitter, driver, twitter_dict)
                time.sleep(5)



# self.gdocs_posted_feeds_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
# self.gcal_posted_feeds_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
# self.pending_posts_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
# self.done_posts_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
# self.failed_posts_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
# self.social_media_button_box.button(QtWidgets.QDialogButtonBox.Apply).setText("Preview")
# self.google_docs_button_box.button(QtWidgets.QDialogButtonBox.Apply).setText("Preview")
# self.google_docs_button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Start")
