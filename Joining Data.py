# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
import statistics as st
import re


# settings for printing in console
width = 320
pd.set_option("display.width", width)
pd.set_option("display.max_rows", 100)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# Read in data
housing = pd.read_csv("housing_after_IEDA.csv")

gemeinde = pd.read_excel("Gemeindeverzeichnis 2020.xlsx", header=0)

# Clean gemeinde
rename_dict = {"Satz-art": "Satzart",
               "Text-kenn-zeichen": "Textkennzeichen",
               "Post-leit-zahl": "Postleitzahl"}


gemeinde.rename(columns=rename_dict,
                inplace=True)

print(gemeinde.head())

# Build dfs with Land and Kreis
ARS_Land = gemeinde[gemeinde.Satzart == "10"][["Gemeindename", "ARS_Land"]]
ARS_Land = ARS_Land.rename(columns = {"Gemeindename": "Bundesland"})
ARS_Kreis = gemeinde[gemeinde.Satzart == "40"][["Gemeindename", "ARS_Land", "ARS_RB", "ARS_Kreis"]]
ARS_Kreis = ARS_Kreis.rename(columns = {"Gemeindename": "Kreis"})

# Filter gemeinde Satzart == 60
gemeinde = gemeinde[gemeinde.Satzart == "60"]

print(gemeinde)

# Join Bundesland and Kreis
gemeinde = pd.merge(gemeinde, ARS_Land, how = "left", on= "ARS_Land")
gemeinde = pd.merge(gemeinde, ARS_Kreis, how = "left", on = ["ARS_Land", "ARS_RB", "ARS_Kreis"])

# Clean gemeindename
gemeinde["Gemeindename"] = gemeinde.Gemeindename.str.split(",").str[0]

# Filter gemeinde with Gemeindenamen from housing
gemeinde = gemeinde[gemeinde.Gemeindename.isin(housing.Place)]
# Find key to join housing and gemeinde

# Join housing and gemeinde
print(gemeinde)



