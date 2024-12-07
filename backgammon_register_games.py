import os
import time 

from dotenv import load_dotenv

from getpass import getpass

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

# webdriver wait and is visible
# https://stackoverflow.com/questions/72754651/attributeerror-webdriver-object-has-no-attribute-find-element-by-xpath

HOST_URL = "https://zooescape.com"
BACKGAMMON_ROOM = HOST_URL + "/backgammon-room.pl"
JOIN_GAME_URL = HOST_URL + "/game-join.pl?v=200"

MINIMUM_CHALLENGE_RATING = 1600
GAME_START_ERROR_MESSAGE = "Unable to start game since"
MAX_GAMES = 280
    
load_dotenv()
PASSWORD = os.getenv("BACKGAMMON_PW")


def log_in(driver):
    
    def attempt_login(driver):
        driver.get("https://zooescape.com")
        driver.find_element("id", "userName").send_keys("codyc4321")
        driver.find_element("id", "password").send_keys(PASSWORD)
        driver.find_element("xpath", "//input[@value='Log in']").click()
        time.sleep(3)

    while True:
        attempt_login(driver)
        page_soup = BeautifulSoup(driver.page_source, "html.parser")
        login_confirmation_tag = page_soup.find("a", id="ze_link_codyc4321")
        if not login_confirmation_tag:
            print("\nSorry, login failed. Try again")
        else:
            break


def determine_active_games(driver):
    print("entering active games now")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    large_divs = soup.find_all("div", class_="large")
    for div in large_divs:
        text = div.text.strip().lower()
        print(text)
        if "my backgammon games" in text:
            print("we got it!")
            games_count_span = div.find("span", class_="xsmall")
            games_count = int(games_count_span.text.replace("(", "").replace(")", "").strip())
            return games_count
        

def get_games_to_join(driver):
    # filter by rating
    driver.get(JOIN_GAME_URL)
    time.sleep(3)
    join_games_soup = BeautifulSoup(driver.page_source, "html.parser")
    relative_games_to_join = []
    a_tags = join_games_soup.find_all("a")
    for a_tag in a_tags:
        text = a_tag.text.strip()
        if text == "Join Now!":
            rating_cell = a_tag.parent.findPrevious("td")
            rating = int(rating_cell.text.strip())
            print(rating)
            username = rating_cell.findPrevious("td").find("a").text.strip()
            if rating > MINIMUM_CHALLENGE_RATING:
                print(f"Acceptable rating of {rating}: adding game w/ user {username}")
                relative_games_to_join.append(a_tag["href"])

    games_to_join = [HOST_URL + x for x in relative_games_to_join]
    return games_to_join


def join_a_game(game_url, driver):
    driver.get(game_url)
    time.sleep(4)
    driver.find_element("xpath", "//input[@value='Join Game']").click()
    driver.get(JOIN_GAME_URL)
    time.sleep(4)


def start_a_new_game(driver):
    driver.get(JOIN_GAME_URL)
    time.sleep(3)
    select = Select(driver.find_element("id", "game_start_rating_min"))
    select.select_by_value(str(MINIMUM_CHALLENGE_RATING))
    driver.find_element("xpath", "//input[@value=' Start Game ']").click()
    if GAME_START_ERROR_MESSAGE in driver.page_source:
        print("games full!")
        time.sleep(5)
        return -1
    else:
        return 1



if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    log_in(driver)
    driver.get(BACKGAMMON_ROOM)
    time.sleep(4)
    active_games = determine_active_games(driver)
    print(active_games)
    print(type(active_games))
    if active_games > MAX_GAMES:
        print("Already have enough games. Exiting now.")
        exit()
    driver.get("https://zooescape.com/backgammon-room.pl")
    time.sleep(3)
    games_to_join = get_games_to_join(driver)

    for game in games_to_join:
        join_a_game(game, driver)

    for index in range(5):
        response = start_a_new_game(driver)
        if response == -1:
            print("can't join any more games")
            break

    driver.close()
