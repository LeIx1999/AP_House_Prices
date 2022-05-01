# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statistics as st
import matplotlib.ticker as mtick

# Read in data
housing_data = pd.read_excel("data/housing.xlsx")

# settings for printing in console
width = 320
pd.set_option("display.width", width)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# First look at the data
print(housing_data.head())

housing_data.info()

print(housing_data.describe())

# Are there missing values?
# NAs
NAS = housing_data.isna().sum().to_frame("Nas")
NAS["Nas"] = NAS["Nas"] / len(housing_data)
NAS["Variablen"] = NAS.index
NAS = NAS.sort_values("Nas", ascending=False)

NAS_plot = sns.barplot(x = NAS[NAS["Nas"] >0].index, y = NAS[NAS["Nas"] >0].Nas)
plt.xlabel("Variablen")
plt.ylabel("Fehlende Werte in Prozent")
plt.title("Fehlende Werte pro Variable in Prozent")
NAS_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.tick_params(axis = "x", rotation = 45)
plt.tight_layout()
plt.show()

# Analyse price
# Histogram of
plt.hist(housing_data.price, density=True, bins = 5)
plt.xlabel("Preis")
plt.ylabel("Häufigkeit")
plt.title("Histogramm der Zielvariable Preis")
plt.show()





