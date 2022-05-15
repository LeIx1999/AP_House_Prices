import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


def get_housing_data(search_term, n_sites):
    """
    This function crawls information about apartments from immowelt.de.
    The function uses a chromedriver to navigate the site and BeautifulSoup to pull data out of the HTML

    Parameters
    ----------
    search_term : str
        The term to search for on immowelt.de
    n_sites : int
        Number of result pages to go through for each search term

    Returns
    ----------
    pandas DataFrame
        A DataFrame with the apartments on the first n_sites result pages containing six columns
        ("Description", "Price", "square-meters", "rooms", "address", "information")
    """
    # Input city to lowercase
    search_term = search_term.lower()

    # URL of target website
    url = "https://www.immowelt.de/"

    # load chrome webdriver with a Service
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

    # call URL
    driver.get(url)

    # look for search bar
    search = driver.find_element(By.ID, 'tbLocationInput')

    # type string in search bar
    search.send_keys(search_term)

    # press return
    search.send_keys(Keys.RETURN)

    # Handling german Umlaute
    character = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for char in character:
        search_term = search_term.replace(char, character[char])

    # wait for site to load
    time.sleep(2)

    # find apartments to click on
    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.find("div", {"class": "SearchList-22b2e"})

    result = []
    # Loop through the first n sites
    for i in range(1, n_sites + 1):
        if i != 1:
            # go to next site
            driver.get(f"https://www.immowelt.de/liste/{search_term}/wohnungen/mieten?d=true&sd=DESC&sf=RELEVANCE&sp={i}")

            time.sleep(2)
            # find next apartments
            soup = BeautifulSoup(driver.page_source, "html.parser")
            items = soup.find("div", {"class": "SearchList-22b2e"})

        # check if there are apartments
        if items is None:
            break

        # Loop through apartments and click all items (loop through children)
        for item in items.children:
            tag_element = item.findChild()

            # check if NoneType
            if tag_element is not None:
                link = tag_element.get("href")
                driver.get(link)
                time.sleep(2)

                # get data
                try:
                    name = driver.find_element(By.XPATH, '// *[ @ id = "aUebersicht"] / h1')
                    price = driver.find_element(By.XPATH,
                                                '//*[@id="aUebersicht"]/app-hardfacts/div/div/div[1]/div[1]/strong')
                    sm = driver.find_element(By.XPATH,
                                                 '//*[@id="aUebersicht"]/app-hardfacts/div/div/div[2]/div[1]/span')
                    rooms = driver.find_element(By.XPATH,
                                                '//*[@id="aUebersicht"]/app-hardfacts/div/div/div[2]/div[2]/span')
                    address = driver.find_element(By.XPATH, '//*[@id="aUebersicht"]/app-estate-address')
                    info_1 = driver.find_element(By.XPATH, '//*[@id="aImmobilie"]/sd-card')

                    result.append([name.get_attribute("textContent"), price.get_attribute("textContent"),
                                   sm.get_attribute("textContent"), rooms.get_attribute("textContent"),
                                   address.get_attribute("textContent"), info_1.get_attribute("textContent")])
                except:
                    print("exception")
    # quit driver
    driver.quit()

    # result as pandas data frame
    result = pd.DataFrame(result, columns=["Description", "Price", "square-meters", "rooms", "address", "information"])
    return (result)


