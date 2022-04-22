import pandas as pd
import numpy as np
import requests
# load crawler data
housing_data = pd.read_excel("housing_data.xlsx")

# Cleaning crawling data
housing_data = housing_data[~housing_data.address.str.contains("Straße nicht freigegeben")]
housing_data["address"] = housing_data.address.str.replace("Auf Karte ansehen", "")

# get lat long from address
coord_list = []

# get first 2000
housing_data = housing_data[:2000]

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

housing_data.to_excel("housing_data_cord1.xlsx")