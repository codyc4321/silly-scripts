import time 

from getpass import getpass

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# webdriver wait and is visible
# https://stackoverflow.com/questions/72754651/attributeerror-webdriver-object-has-no-attribute-find-element-by-xpath

HOST_URL = "https://zooescape.com"

JOIN_GAME_URL = "https://zooescape.com/game-join.pl?v=200"

MINIMUM_CHALLENGE_RATING = "1675"

GAME_START_ERROR_MESSAGE = "Unable to start game since"


def log_in(driver):
    driver.get("https://zooescape.com")
    driver.find_element("id", "userName").send_keys("codyc4321")
    password = getpass("Please enter your password: ")
    driver.find_element("id", "password").send_keys(password)
    driver.find_element("xpath", "//input[@value='Log in']").click()


def get_games_to_join(driver):
    # filter by rating
    driver.get(JOIN_GAME_URL)
    time.sleep(3)
    join_games_soup = BeautifulSoup(driver.page_source)
    relative_games_to_join = []
    a_tags = join_games_soup.find_all("a")
    for a_tag in a_tags:
        text = a_tag.text.strip()
        if text == "Join Now!":
            rating_cell = a_tag.parent.findPrevious("td")
            rating = int(rating_cell.text.strip())
            print(rating)
            username = rating_cell.findPrevious("td").find("a").text.strip()
            if rating > 1650:
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
    select.select_by_value(MINIMUM_CHALLENGE_RATING)
    driver.find_element("xpath", "//input[@value=' Start Game ']").click()
    if GAME_START_ERROR_MESSAGE in driver.page_source:
        print("games full!")
        time.sleep(5)
        return -1
    else:
        return 1



driver = webdriver.Chrome()
log_in(driver)
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
