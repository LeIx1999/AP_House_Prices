import pandas as pd
import numpy as np
import requests
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

# settings for printing in console
width = 320
pd.set_option("display.width", width)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# load crawler data
housing_data = pd.read_excel("housing_data.xlsx")

# Cleaning crawling data
housing_data = housing_data[~housing_data.address.str.contains("Straße nicht freigegeben")]
housing_data["address"] = housing_data.address.str.replace("Auf Karte ansehen", "")

# get lat long from address
coord_list = []

# subset due to api limitations (2.5k per day)
housing_data = housing_data[4000:len(housing_data)]

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

# saving as xlsx.
housing_data.to_excel("data/housing_data_cord1.xlsx")

# read in xlsx
housing_data = pd.read_excel("data/housing_data_cord.xlsx")

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
        gem_key.append(gemeinde_data["AGS"][bool_index])
    except:
        gem_key.append("")

housing_data["gem_20"] = gem_key

# load regiostar data
regiostar = pd.read_excel("data/regiostar-referenzdateien.xlsx", sheet_name = "ReferenzGebietsstand2020")

# add leading zero to key
regiostar["gem_20"] = [f"0{str(x)}" for x in regiostar["gem_20"]]


# join regiostar
housing_data = pd.merge(housing_data, regiostar.loc[:, ["gem_20", "RegioStaR7"]], how = "left", on = "gem_20")

housing_data["RegioStaR7"] = housing_data["RegioStaR7"].replace({71: "Metropole",
                                                                 72: "Regiopole",
                                                                 73: "Großstadt",
                                                                 74: "Zentrale Stadt",
                                                                 75: "Mittelstadt",
                                                                 76: "Städtischer Raum",
                                                                 77: "Kleinstädtischer, dörflicher Raum"})


