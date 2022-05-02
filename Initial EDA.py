# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statistics as st
import matplotlib.ticker as mtick

# Read in data
housing_data = pd.read_excel("data/housing.xlsx", index_col=0, decimal = ",")
housing_data["floor"] = housing_data["floor"].astype("string")


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
NAS = pd.DataFrame({"variable": NAS.index, "percentage": NAS.Nas / len(housing_data)})
NAS = NAS[NAS["percentage"] >0]
NAS = NAS.sort_values("percentage", ascending=False).reset_index()

# Plot NAs
NAS_plot= sns.barplot(x = "variable", y = "percentage", data = NAS)
for index, value in enumerate(NAS.percentage):
    plt.text(index, value,
             f"{value:.1%}", ha = "center")
plt.xlabel("Variablen")
plt.ylabel("Fehlende Werte in Prozent")
plt.title("Fehlende Werte pro Variable in Prozent")
NAS_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.tick_params(axis = "x", rotation = 45)
plt.tight_layout()
plt.show()

# Analyse price
# Outlier?
price_boxplot = plt.boxplot(housing_data.price)
plt.xlabel("Wohnungspreis")
plt.title("Boxplot der Wohnungspreise")
plt.show()

# Remove extreme outliers
per25, per75 = np.percentile(housing_data.price, [25, 75])
extreme_outlier = (per75 - per25) * 3 + per75
outliers = price_boxplot["fliers"][0].get_data()[1]

housing_data = housing_data[housing_data["price"] <= extreme_outlier]

# Histogram of price
plt.hist(housing_data.price, density=True, bins = 20, color = "b", edgecolor = "k")
plt.axvline(housing_data.price.mean(), color = "r", linestyle = "dashed")
plt.xlabel("Preis")
plt.ylabel("Häufigkeit")
plt.title("Histogramm der abhängigen Variable Preis")
plt.show()

# Verteilung aller erklärenden Variablen in einem Plot

plt.style.use("default")
# square-meters
plt.subplot(3, 3, 1)
housing_data = housing_data[housing_data["square-meters"] != "kA"]
housing_data["square-meters"] = housing_data["square-meters"].astype("float")
plt.hist(housing_data["square-meters"], density=True, bins = 20, color = "b", edgecolor = "k")
plt.axvline(housing_data["square-meters"].mean(), color = "r", linestyle = "dashed")
plt.xlabel("Quadratmeter")
plt.ylabel("Häufigkeit")
plt.title("Histogramm der unabhängigen Variable Quadratmeter")

# rooms
rooms = housing_data.groupby("rooms")["rooms"].count().to_frame()
rooms = pd.DataFrame({"value": rooms.index, "percentage": rooms.rooms / len(housing_data)})
rooms = rooms[rooms["percentage"] >= 0.001]
rooms = rooms.sort_values("percentage", ascending = False).reset_index()

plt.subplot(3, 3, 2)
rooms_plot= sns.barplot(x = "value", y = "percentage", data = rooms)
for index, value in enumerate(rooms.percentage):
    plt.text(index, value,
             f"{value:.1%}", ha = "center")
plt.xlabel("Räume")
plt.ylabel("Häufigkeit in Prozent")
plt.title("Säulendiagramm der unabhängigen Variable Räume")
rooms_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.tick_params(axis = "x", rotation = 45)
plt.tight_layout()

# RegioStaR7
regio = housing_data.groupby("RegioStaR7")["RegioStaR7"].count().to_frame()
regio = pd.DataFrame({"value": regio.index, "percentage": regio.RegioStaR7 / len(housing_data)})
regio = regio[regio["percentage"] >= 0.001]
regio = regio.sort_values("percentage", ascending = False).reset_index()

plt.subplot(3, 3, 3)
regio_plot = sns.barplot(x = "value", y = "percentage", data = regio)
for index, value in enumerate(regio.percentage):
    plt.text(index, value,
             f"{value:.1%}", ha = "center")
plt.xlabel("RegioStaR7")
plt.ylabel("Häufigkeit in Prozent")
plt.title("Säulendiagramm der unabhängigen Variable RegioStaR7")
regio_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.tick_params(axis = "x", rotation = 45)
plt.tight_layout()

plt.subplot(3, 3, 4)
# gem_size_km2
plt.hist(housing_data["gem_size_km2"], density=True, bins = 20, color = "b", edgecolor = "k")
plt.axvline(housing_data["gem_size_km2"].mean(), color = "r", linestyle = "dashed")
plt.xlabel("Quadratmeter der Gemeinde")
plt.ylabel("Häufigkeit")
plt.title("Histogramm der unabhängigen Variable Quadratmeter der Gemeinde")

plt.subplot(3, 3, 5)
# gem_population
plt.hist(housing_data["gem_population"], density=True, bins = 20, color = "b", edgecolor = "k")
plt.axvline(housing_data["gem_population"].mean(), color = "r", linestyle = "dashed")
plt.xlabel("Bevölkerung der Gemeinde")
plt.ylabel("Häufigkeit")
plt.title("Histogramm der unabhängigen Variable Bevölerung der Gemeinde")
plt.tight_layout()


# balcony
balcony = housing_data.groupby("balcony")["balcony"].count().to_frame()
balcony = pd.DataFrame({"value": balcony.index, "percentage": balcony.balcony / len(housing_data)})
balcony = balcony[balcony["percentage"] >= 0.001]
balcony = balcony.sort_values("percentage", ascending = False).reset_index()

plt.subplot(3, 3, 6)
balcony_plot = sns.barplot(x = "value", y = "percentage", data = balcony)
for index, value in enumerate(balcony.percentage):
    plt.text(index, value,
             f"{value:.1%}", ha = "center")
plt.xlabel("Balkon")
plt.ylabel("Häufigkeit in Prozent")
plt.title("Säulendiagramm der unabhängigen Variable Balkon")
balcony_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.tick_params(axis = "x", rotation = 45)
plt.tight_layout()

# floor
floor = housing_data.groupby("floor")["floor"].count().to_frame()
floor = pd.DataFrame({"value": floor.index, "percentage": floor.floor / len(housing_data)})
floor = floor[floor["percentage"] >= 0.001]
floor = floor.sort_values("percentage", ascending = False).reset_index()

plt.subplot(3, 3, 7)
floor_plot = sns.barplot(x = "value", y = "percentage", data = floor)
for index, value in enumerate(floor.percentage):
    plt.text(index, value,
             f"{value:.1%}", ha = "center")
plt.xlabel("Geschoss")
plt.ylabel("Häufigkeit in Prozent")
plt.title("Säulendiagramm der unabhängigen Variable Geschoss")
floor_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.tick_params(axis = "x", rotation = 45)
plt.tight_layout()
plt.show()