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

housing_data["lat"] = [appartement["lat"] for appartement in coord_list]
housing_data["lon"] = [appartement["lng"] for appartement in coord_list]

# saving as xlsx.
housing_data.to_excel("housing_data_cord1xlsx")

# read in xlsx
housing_data = pd.read_excel("housing_data_cord.xlsx")

# read in shapefile data
gemeinde_data = gpd.read_file("vg250_01-01.gk3.shape.ebenen/vg250_ebenen_0101/VG250_GEM.shp")

# get gemeinde key from shapefile data
gem_key = []
for index, row in housing_data.iterrows():
    cord_point = Point(row.lat, row.long)
    bool_list = gemeinde_data.contains(cord_point)

    bool_index = bool_list.index(True)
    gem_key.append(gemeinde_data["AGS"][bool_index])



