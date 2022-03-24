# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read in data
housing = pd.read_csv("germany_housing_data_14.07.2020.csv")

# settings for printing in console
width = 320
pd.set_option("display.width", width)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# Inspect data
print(housing.head())

housing.info()

print(housing.describe())

# Variables
print(housing.columns)

# Unnamed as index
housing.set_index('Unnamed: 0')

# NAs
NAS = housing.isna().sum().to_frame("Nas")
NAS["Nas"] = NAS["Nas"] / len(housing)
NAS = NAS.sort_values("Nas", ascending=False)
print(NAS)

# Plot Nas
#NAS.plot(kind = "bar")


# Analyse price
housing["Price"].plot(kind = "hist", xlim = (0, 9000000))
plt.show()