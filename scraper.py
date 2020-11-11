from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

import matplotlib.pyplot as plt
from matplotlib.dates import drange
import numpy as np
import time
import datetime

def load_settings():
    settings = {
        'browser': 'firefox',
        'browser_path': '/home/josua/.mozilla/firefox/3v4idfl6.webscraping',
        'page': 'https://web.whatsapp.com/'
    }
    return settings


def load_driver(settings):
    firefox_profile = webdriver.FirefoxProfile(settings['browser_path'])
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(firefox_profile, options=options)
    return driver

def open_chat(driver, name):
    search_field = driver.find_element_by_xpath('//div[text() = "Suchen oder neuen Chat beginnen"]/parent::div/descendant::div[@contenteditable="true"]')
    search_field.send_keys(name)
    found = False
    while not found:
            try:
                chat = driver.find_element_by_xpath('//span[@title = "{}"]'.format(name))
                found = True
            except:
                found = False
    
    chat.click()

def send_message(driver, username, message, count):
    open_chat(driver, username)

    msg_box = driver.find_element_by_xpath('//div[@spellcheck = "true"]')
    for _ in range(count):
        msg_box.send_keys(message)
        button = driver.find_element_by_xpath('//span[@data-icon="send"]/parent::button')

        button.click()

def scroll_upwards(driver, scroll_time):
    message_area = driver.find_element_by_xpath(
        "//div[contains(@class, 'z_tTQ')]"
    )
    message_area.click()
    time.sleep(1)
    for _ in range(scroll_time * 10):
        time.sleep(0.1)
        message_area.send_keys(Keys.PAGE_UP)

    processed_messages = []
    for raw_message in driver.find_elements_by_xpath(
            "//div[contains(@class,'focusable-list-item')]"):
        #message_list.append(message)
        classes = raw_message.get_attribute("class")
        if "message" in classes:
            message_dict = {}
            text, emojis, sender, date_time = extract_message(raw_message)
            message_dict["text"] = text
            message_dict["emojis"] = emojis
            message_dict["sender"] = sender
            message_dict["datetime"] = date_time
            if message_dict["sender"] != "unknown" and message_dict not in processed_messages:
                processed_messages.append(message_dict)

    return processed_messages

def extract_message(raw_message):
    """
    get infos from html
    """
    try:
        message_container = raw_message.find_element_by_xpath(
            ".//div[@class='copyable-text']")
        meta_raw = message_container.get_attribute("data-pre-plain-text")
        rawdatetime, sender = meta_raw.split("] ")
        sender = sender[:-2]
        time, date = rawdatetime[1:].split(", ")
        day, month, year = date.split(".")
        hour, minute = time.split(":")
        date_time = datetime.datetime(int(year), int(month), int(day), hour=int(hour), minute=int(minute))
        messagetext = message_container.find_element_by_xpath(
            ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
        ).text
        emojis = []
        for emoji in message_container.find_elements_by_xpath(
                ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
        ):
            emojis.append(emoji.get_attribute("data-plain-text"))
    except:
        messagetext, emojis, sender, date_time = "no text found", [], "unknown", datetime.date(1970,1,1)
    
    return messagetext, emojis, sender, date_time


def wait_for_loading(driver):
    loaded = False
    while not loaded:
        try:
            driver.find_element_by_xpath('//div[text() = "Suchen oder neuen Chat beginnen"]/parent::div/descendant::div[@contenteditable="true"]')
            loaded = True
        except:
            loaded = False





def plot_per_hour(processed_messages):
    x = np.arange(24)
    total = np.zeros(24)

    people = {}

    for message_dict in processed_messages:
        hour = message_dict["datetime"].hour
        total[hour] += 1
        sender = message_dict["sender"]
        if sender not in people:
            people[sender] = np.zeros(24)
        
        people[sender][hour] += 1

    for sender in people:
        plt.plot(x, people[sender], label=sender)
    #plt.plot(x, total, label="total messages")
    plt.legend()
    plt.show()

def plot_per_day(processed_messages):
    people = {}
    date1 = processed_messages[0]["datetime"].date()
    date2 = datetime.date.today()
    dates = drange(date1, date2, delta=datetime.timedelta(days=1))
    total = np.zeros(len(dates))
    for message_dict in processed_messages:
        thisdate = message_dict["datetime"].date()
        difference = thisdate - date1
        index = difference.days -1
        total[index] += 1
        sender = message_dict["sender"]
        if sender not in people:
            people[sender] = np.zeros(len(dates))
        
        people[sender][index] += 1
    
    #plt.plot_date(dates, total, ls="-", marker=",", label="total messages")
    for sender in people:
        plt.plot_date(dates, people[sender], ls="-", marker=",", label=sender)
    
    plt.legend()
    plt.show()

settings = load_settings()
driver = load_driver(settings)
driver.get(settings['page'])
print("loading website")
wait_for_loading(driver)
print("website loaded")

#do something here:

open_chat(driver, "FHSZ")
#send_message(driver, "Meine Gruppe", "Test", 1)
processed_messages = scroll_upwards(driver, 100)

import pickle
with open("fhsz_chat", "wb") as f:
    pickle.dump(processed_messages, f)

#plot_per_hour(processed_messages)
#plot_per_day(processed_messages)