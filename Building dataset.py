import nltk
import pandas as pd
import numpy as np
import requests
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
import requests
from numpy import nan
import collections
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# settings for printing in console
width = 320
pd.set_option("display.width", width)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# load crawler data
housing_data = pd.read_excel("data/housing_data.xlsx")

# Cleaning crawling data
housing_data = housing_data[~housing_data.address.str.contains("Straße nicht freigegeben")]
housing_data["address"] = housing_data.address.str.replace("Auf Karte ansehen", "")

# get lat long from address
coord_list = []

# subset due to api limitations (2.5k per day)
# housing_data = housing_data[:2500]
housing_data = housing_data[:1]

for index, row in housing_data.iterrows():
    link = f"https://api.opencagedata.com/geocode/v1/json?q={row.address}&key=bde3b179622541a9b24545f02697e461"
    response = requests.get(link)
    try:
        response = response.json()["results"][0]["geometry"]
    except:
        response = {"lat": 0,
                    "lng": 0}
    coord_list.append(response)

# create columns lat and lon
housing_data["lat"] = [appartement["lat"] for appartement in coord_list]
housing_data["lon"] = [appartement["lng"] for appartement in coord_list]

# read in xlsx
housing_data = pd.read_excel("data/housing_data_cords.xlsx")

# read in shapefile data
gemeinde_data = gpd.read_file("data/vg250_01-01.gk3.shape.ebenen/vg250_ebenen_0101/VG250_GEM.shp")

# set the crs (coordinate reference system)
gemeinde_data = gemeinde_data.to_crs("EPSG:4326")

# get gemeinde key from shapefile data
gem_key = []

# iterate through coordinates and get gemeinde key
for index, row in housing_data.iterrows():
    cord_point = Point(row.lon, row.lat)
    bool_list = gemeinde_data.contains(cord_point)
    try:
        bool_index = bool_list[bool_list == True].index.values[0]
        gem_key.append(gemeinde_data["SDV_ARS"][bool_index])
    except:
        gem_key.append("")

housing_data["gemrs_20"] = gem_key

# load regiostar data
regiostar = pd.read_excel("data/regiostar-referenzdateien.xlsx", sheet_name = "ReferenzGebietsstand2020")

regiostar["gemrs_20"] = regiostar.gemrs_20.astype("string")

# remove leading zeros
housing_data["gemrs_20"] = [x.lstrip("0") for x in housing_data["gemrs_20"]]


# join regiostar
housing_data = pd.merge(housing_data, regiostar.loc[:, ["gemrs_20", "RegioStaR7"]], how = "left", on = "gemrs_20")

# make var explainable
housing_data["RegioStaR7"] = housing_data["RegioStaR7"].replace({71: "Metropole",
                                                                 72: "Regiopole",
                                                                 73: "Großstadt",
                                                                 74: "Zentrale Stadt",
                                                                 75: "Mittelstadt",
                                                                 76: "Städtischer Raum",
                                                                 77: "Kleinstädtischer, dörflicher Raum"})

# clean df
housing_data = housing_data.loc[:, "Description":]

# fill to 12 digits
housing_data["gemrs_20"] = [x.zfill(12) for x in housing_data["gemrs_20"]]

# clean gemrs_20
housing_data["gemrs_20"] = [x[0:9] for x in housing_data["gemrs_20"]]

# Join Bevölkerung
bev_data = pd.read_excel("data/Gemeindeverzeichnis 2020.xlsx", dtype = {"gem_20": str})
bev_data = bev_data[~bev_data["Bev_Insgesamt"].isna()]

housing_data = pd.merge(housing_data, bev_data[["gem_20", "Fläche km2 ", "Bev_Insgesamt"]], how = "left", left_on = "gemrs_20", right_on = "gem_20")

# Rename
housing_data = housing_data.rename(columns= {"Fläche km2 ": "gem_size_km2",
                                             "Bev_Insgesamt": "gem_population",
                                             "Description": "description",
                                             "Price": "price",
                                             "RegioStarR7": "regioStarR7"})

housing_data = housing_data.drop(columns=["gem_20", "gemrs_20"])

# remove duplicates
housing_data = housing_data.drop_duplicates(subset = ["description", "price", "address", "square-meters"])

# add a few variables
housing_data["balcony"] = ["Balkon" in x or "balkon" in x for x in housing_data["information"]]

housing_data["floor"] = [x[x.find("Geschoss") - 3:x.find("Geschoss")-2] for x in housing_data["information"]]

# Erdgeschoss
floor = []
for index, row in housing_data.iterrows():
    if row["floor"].isnumeric():
        floor.append(row["floor"])
    else:
        floor.append("Erdgeschoss" in row["information"] or "erdgeschoss" in row["information"])

housing_data["floor"] = floor

# Ergeschoss = 0, missing = nan
housing_data["floor"] = [nan if x == False else 0 if x == True else x for x in housing_data["floor"]]

# no need for information and address anymore
housing_data = housing_data.drop(columns=["information", "address"])

# clean price
housing_data["price"] = [float(x) if any(char.isdigit() for char in x) else 0 for x in housing_data.price]
housing_data = housing_data[housing_data["price"] >0]

# Number of words per Desription
housing_data = housing_data[~housing_data["description"].isna()]
housing_data["description"] = housing_data["description"].astype("string")
housing_data["des_length"] = [len(des.split()) for des in housing_data["description"]]

housing_data = housing_data.drop(columns="description")

# Most common words
# nltk.download("stopwords")
# des_string = " ".join([des for des in list(housing_data["description"])])
# des_tokens = word_tokenize(des_string)
# stopwords = stopwords.words("german")
# des_tokens = [word for word in des_tokens if not word in stopwords]
# word_counts = collections.Counter(des_tokens)



housing_data.to_excel("data/housing.xlsx")