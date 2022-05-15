# Import packages
import collections

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
from matplotlib.ticker import PercentFormatter
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
# Read in data
housing_data = pd.read_excel("data/housing.xlsx", index_col=0, decimal = ",")
housing_data["floor"] = housing_data["floor"].astype("string")
housing_data = housing_data[housing_data["square-meters"] != "kA"]
housing_data["square-meters"] = housing_data["square-meters"].astype("float64")
housing_data = housing_data[housing_data["rooms"] != "k.A."]
housing_data["rooms"] = housing_data["rooms"].astype("float64")


# settings for printing in console
width = 320
pd.set_option("display.width", width)
np.set_printoptions(linewidth=width)
pd.set_option("display.max_columns", 30)

# First look at the data
print(housing_data.head())

housing_data.info()

print(housing_data.describe())


# Analyse price
# Outlier?
price_boxplot = plt.boxplot(housing_data.price)
plt.xlabel("price")
plt.title("Boxplot price")
plt.show()

# Remove outliers and nans
housing_data = housing_data[~housing_data["price"].isnull()]
per25, per75 = np.percentile(housing_data.price, [25, 75])
outlier = (per75 - per25) * 1.5 + per75

housing_data = housing_data[housing_data["price"] <= outlier]


# Function Histogramm
def histo(data, var):
    """
    This function creates a histogram based on the variable specified in var.
    The y-axis shows the relation as percentage. The red line marks the median value of var.

    Parameters
    ----------
    data : pandas DataFrame
        The dataset containing var
    var : str
        The variable to plot a histogram with

    Returns
    ----------
    matplotlib pyplot
        A histogram showing the distribution of the variable var
    """
    plt.hist(data[var], bins=20, color="b", edgecolor="k", weights=np.ones(len(data[var])) / len(data[var]))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.axvline(data[var].median(), color="r", linestyle="dashed")
    plt.xlabel(var)
    plt.ylabel("Count %")
    plt.title(f'Histogram {var}')
    plt.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.show()

# Histogram of price
histo(housing_data, "price")

# Remove obvious outliers and clean data
housing_data = housing_data[housing_data["square-meters"] <= 500]
housing_data = housing_data[housing_data["rooms"] < 7.0]
housing_data = housing_data[housing_data["rooms"] != 2.1]

# Encode RegioStaR7
encoder = LabelEncoder()
housing_data["RegioStaR7"] = encoder.fit_transform(housing_data["RegioStaR7"])


# Verteilung aller erklärenden Variablen in einem Plot
plt.style.use("default")

# square-meters
plt.subplot(3, 3, 1)
housing_data = housing_data[housing_data["square-meters"] != "kA"]
housing_data["square-meters"] = housing_data["square-meters"].astype("float")
histo(housing_data, "square-meters")

plt.subplot(3, 3, 2)
# gem_size_km2
histo(housing_data, "gem_size_km2")

plt.subplot(3, 3, 3)
# gem_population
histo(housing_data[housing_data["gem_population"] < 1000000], "gem_population")

# des_length
plt.subplot(3, 3, 4)
histo(housing_data, "des_length")

# function bar chart
def bar(data, var):
    """
    This function creates a bar chart based on the variable specified in var.
    The y-axis shows the relation as percentage.

    Parameters
    ----------
    data : pandas DataFrame
        The dataset containing var
    var : str
        The variable to plot a bar chart with

    Returns
    ----------
    matplotlib pyplot
        A bar chart showing the distribution of the variable var
    """
    df = data.groupby(var)[var].count().to_frame()
    df = pd.DataFrame({"value": df.index, "percentage": df[var] / len(data)})
    df = df[df["percentage"] >= 0.001]
    df = df.sort_values("percentage", ascending=False).reset_index()
    df["value"] = df["value"].astype("string")
    df = df[df["percentage"] >= 0.01]

    df_plot = sns.barplot(x="value", y="percentage", data=df)
    for index, value in enumerate(df.percentage):
        plt.text(index, value + 0.001,
                 f"{value:.1%}", ha="center")
    plt.xlabel(var)
    plt.ylabel("Count %")
    plt.ylim(0, df["percentage"][0] + 0.05)
    plt.title(f'Barchart {var}')
    df_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
    plt.tick_params(axis="x", rotation=45)
    plt.tight_layout()


# rooms
plt.subplot(3, 3, 5)
bar(housing_data, "rooms")

# RegioStaR7
plt.subplot(3, 3, 6)
bar(housing_data, "RegioStaR7")

# balcony
plt.subplot(3, 3, 7)
bar(housing_data, "balcony")

# floor
plt.subplot(3, 3, 8)
bar(housing_data, "floor")

plt.subplots_adjust(wspace=0.35, hspace=0.35)
plt.suptitle("Distribution variables")



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

# Are there missing values?
# NAs
housing_data.info()
NAS = housing_data.isna().sum().to_frame("Nas")
NAS = pd.DataFrame({"variable": NAS.index, "percentage": (NAS.Nas / len(housing_data))* 100})
NAS = NAS[NAS["percentage"] >0]
NAS = NAS.sort_values("percentage", ascending=False).reset_index()

# Remove the few gem_size_km2 and gem_population nas
housing_data = housing_data[~housing_data["gem_size_km2"].isna()]

# There are too many nas in floor to remove all of them
# Fill with median
housing_data["floor"] = housing_data["floor"].astype("float")
housing_data["floor"].fillna(housing_data["floor"].median(), inplace=True)

# There are no nas left
housing_data.info()

# Understanding relationships
# Price and all other variables
# scatter function
def scatter_plot(data, var_x, var_y):
    """
    This function creates a scatter plot with var_x on the x-axis and var_y on the y-axis.

    Parameters
    ----------
    data : pandas DataFrame
        The dataset containing var_x and var_y
    var_x : str
        The variable on the x-axis
    var_y : str
        The variable on the y-axis

    Returns
    ----------
    matplotlib pyplot
        A scatter plot with the variables var_x and var_y
    """
    plt.scatter(x=var_x, y=var_y, data = data)
    plt.xlabel(var_x)
    plt.ylabel(var_y)
    plt.title(f'Scatterplot {var_x} & {var_y}')
    plt.tight_layout()

# boxplot function
def box(data, var_x, var_y):
    """
    This function creates a boxplot with var_x on the x-axis and var_y on the y-axis.

    Parameters
    ----------
    data : pandas DataFrame
        The dataset containing var_x and var_y
    var_x : str
        The variable on the x-axis
    var_y : str
        The variable on the y-axis

    Returns
    ----------
    matplotlib pyplot
        A boxplot with the variables var_x and var_y
    """
    order = data.groupby(var_x).median().sort_values(var_y)
    sns.boxplot(x=var_x, y = var_y, order = order.index, data = data)
    plt.xlabel(var_x)
    plt.ylabel(var_y)
    plt.title(f'Boxplot {var_x} & {var_y}')
    plt.tight_layout()


plt.style.use("default")
# square-meters
plt.subplot(4, 3, 1)
scatter_plot(housing_data, "square-meters", "price")

# lat
plt.subplot(4, 3, 2)
scatter_plot(housing_data, "lat", "price")

# lon
plt.subplot(4, 3, 3)
scatter_plot(housing_data, "lon", "price")

# gem_size_km2
plt.subplot(4, 3, 4)
scatter_plot(housing_data, "gem_size_km2", "price")

# gem_population
plt.subplot(4, 3, 5)
scatter_plot(housing_data, "gem_population", "price")

# des_length
plt.subplot(4, 3, 6)
scatter_plot(housing_data, "des_length", "price")

# rooms
plt.subplot(4, 3, 7)
box(housing_data, "rooms", "price")

# RegiostaR7
plt.subplot(4, 3, 8)
box(housing_data, "RegioStaR7", "price")

# balcony
plt.subplot(4, 3, 9)
box(housing_data, "balcony", "price")

# floor
plt.subplot(4, 3, 10)
box(housing_data, "floor", "price")

plt.subplots_adjust(wspace=0.35, hspace=0.35)
plt.suptitle("Compare price to the other variables")

housing_data.to_excel("data/housing_data_prepped.xlsx")

