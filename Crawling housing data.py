from Webcrawler import get_housing_data
import pandas as pd
import numpy as np
# settings for printing in console
width = 320
pd.set_option("display.width", width)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# get germanys biggest city as crawler input
cities = pd.read_excel("data/Gemeindeverzeichnis 2020.xlsx")

# Only bigger cities
cities = cities[cities["Satz-art"] == "40"]

# Prepare for crawler
cities = list(cities["Gemeindename"].str.split(",").str[0])
cities = cities[:100]

# Call crawler function on citys
housing_data_list = [get_housing_data(city, 5) for city in cities]

housing_data = pd.concat(housing_data_list)

# clean price and sm
housing_data["Price"] = housing_data["Price"].apply(lambda x: x.replace("€", "").replace(".", "").replace(",", "."))
housing_data["square-meters"] = housing_data["square-meters"].apply(lambda x: x.replace("m²", "").replace(".", "").replace(",", "."))

# Excel
housing_data.to_excel("housing_data.xlsx")







