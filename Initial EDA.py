# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn

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
housing = housing.set_index('Unnamed: 0')

# NAs
NAS = housing.isna().sum().to_frame("Nas")
NAS["Nas"] = NAS["Nas"] / len(housing)
NAS = NAS.sort_values("Nas", ascending=False)


# Plot Nas
NAS.plot(kind = "bar")
#plt.show()

# Analyse price
# Histogram of
plt.hist(housing.Price, density=True, bins = 30, range = (0, np.quantile(housing.Price, 0.95)))
plt.xlabel("Price")
plt.ylabel("Probability")
plt.title("Histogram of Price")
#plt.show()

# Probably no log transformation needed
price_box = plt.boxplot(housing.Price)
#plt.show()

# Remove outliers !?
outliers = price_box["fliers"][0].get_data()[1]
housing = housing[~housing.Price.isin(outliers)]

# Correlations with price
corr_Matrix = housing.corr()
corr_Matrix_Price = corr_Matrix.sort_values("Price", ascending=False).Price
print(corr_Matrix_Price)

# Visualize
sn.heatmap(corr_Matrix, annot = True)
#plt.show()
print(housing.columns)

# Not to much correlation going on

# Look at living space a obvious correlation
var_num = "Living_space"
housing.plot.scatter(x = var_num, y = "Price", xlim = ((0, 1500)))

plt.show()

# Look at the categorical features
var_cat = "Type"

order = housing.groupby("Type").Price.mean().sort_values().to_frame("Price").index

sn.boxplot(x = var_cat, y = "Price", data = housing, order = order)
plt.show()











