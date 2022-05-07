# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statistics as st
import matplotlib.ticker as mtick
import folium
from folium.plugins import MarkerCluster
import branca
import branca.colormap as cm

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

# Function Histogramm
def histo(var, xlabel, ylabel, title):
    plt.hist(var, density=True, bins=20, color="b", edgecolor="k")
    plt.axvline(var.median(), color="r", linestyle="dashed")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()

# Histogram of price
histo(housing_data.price, "Preis", "Häufigkeit", "Histogramm der abhängigen Variable Preis")

# Verteilung aller erklärenden Variablen in einem Plot

plt.style.use("default")
# square-meters
plt.subplot(3, 3, 1)
housing_data = housing_data[housing_data["square-meters"] != "kA"]
housing_data["square-meters"] = housing_data["square-meters"].astype("float")
histo(housing_data[housing_data["square-meters"] <= 500]["square-meters"], "Quadratmeter", "Häufigkeit", "Histogramm Quadratmeter")

# function bar chart
def bar(data, var,  xlabel, ylabel, title):
    df = data.groupby(var)[var].count().to_frame()
    df = pd.DataFrame({"value": df.index, "percentage": df[var] / len(data)})
    df = df[df["percentage"] >= 0.001]
    df = df.sort_values("percentage", ascending=False).reset_index()

    df_plot = sns.barplot(x="value", y="percentage", data=df)
    for index, value in enumerate(df.percentage):
        plt.text(index, value,
                 f"{value:.1%}", ha="center")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    df_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
    plt.tick_params(axis="x", rotation=45)
    plt.tight_layout()

# rooms
plt.subplot(3, 3, 2)
bar(housing_data, "rooms", "Räume", "Häufigkeit in Prozent", "Säulendiagramm Räume")

# RegioStaR7
plt.subplot(3, 3, 3)
bar(housing_data, "RegioStaR7", "RegioStaR7", "Häufigkeit in Prozent", "Säulendiagramm RegioStaR7")

plt.subplot(3, 3, 4)
# gem_size_km2
histo(housing_data["gem_size_km2"], "Quadratmeter der Gemeinde", "Häufigkeit", "Histogramm Quadratmeter der Gemeinde")

plt.subplot(3, 3, 5)
# gem_population
histo(housing_data[housing_data["gem_population"] < 1000000]["gem_population"], "Bevölkerung der Gemeinde", "Häufigkeit", "Histogramm Bevölerung der Gemeinde")

# balcony
plt.subplot(3, 3, 6)
bar(housing_data, "balcony", "Balkon", "Häufigkeit in Prozent", "Säulendiagramm Balkon")

# floor
plt.subplot(3, 3, 7)
bar(housing_data, "floor", "Geschoss", "Häufigkeit in Prozent", "Säulendiagramm Geschoss")


# Plot lat long with Folium and Leaflet
# https://www.earthdatascience.org/tutorials/introduction-to-leaflet-animated-maps/
germany_coords = [51.163361, 10.447683]

# build map
germany_map = folium.Map(location=germany_coords, zoom_start=7)

# add flats
for index, row in housing_data.iterrows():
    folium.Marker(location=[row["lat"], row["lon"]]).add_to(germany_map)

# save map
germany_map.save("germany_map.html")

# There are flats outside of germany
# Remove those
# bb of germany
housing_data = housing_data[housing_data["lat"].between(47.3024876979, 54.983104153) &
                            housing_data["lon"].between(5.98865807458, 15.0169958839)]


# Price and lat lon
# https://medium.com/analytics-vidhya/create-and-visualize-choropleth-map-with-folium-269d3fd12fa0
# build map
germany_map_price = folium.Map(location=germany_coords, zoom_start=7)

# create color palette
palette = cm.LinearColormap(colors=["yellow", "red"],
                            vmin = housing_data.price.min(), vmax=housing_data.price.max())

# add flats
for index, row in housing_data.iterrows():
    folium.CircleMarker(location=[row["lat"], row["lon"]], radius = 14,
                  fill = True, color = palette(row["price"]), popup = str(row["price"])).add_to(germany_map_price)

germany_map_price.add_child(palette)
# save map
germany_map_price.save("germany_map_price.html")

# Fill missing values

# Price and all other variables
sns.pairplot(housing_data.loc[:, "price":], palette = "icefire", hue = "price", diag_kind = None)
plt.draw()