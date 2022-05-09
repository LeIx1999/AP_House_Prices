# Import packages
import pandas as pd
import math
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

housing_data = pd.read_excel("data/housing_data_prepped.xlsx", index_col=0, decimal = ",")
housing_data = housing_data[~housing_data["description"].isnull()]

# Encode RegioStaR7 and Description
encoder = LabelEncoder()
housing_data["RegioStaR7"] = encoder.fit_transform(housing_data["RegioStaR7"])

tfidf_vectorizer = TfidfVectorizer()
tfidf_vectorizer.fit_transform(housing_data["description"])
housing_data = housing_data.drop(columns = "description")

housing_data = housing_data.dropna()

# train and test split
housing_train, housing_test = train_test_split(housing_data,
                                               test_size=0.33,
                                               random_state=3)

# Random Forest with Cross Validation
housing_DT = RandomForestRegressor(random_state=3)
housing_params = {"min_samples_split": [2, 4, 6],
                  "max_features": [6, 7, 8],
                  "max_samples": [0.5, 0.6, 0.7,  0.8],
                  "max_depth": [10, 12, 14]}

housing_CV = GridSearchCV(housing_DT, housing_params, cv = 3)

# create fit
housing_CV.fit(housing_train.drop(columns="price"), housing_train["price"])
housing_CV_res = pd.DataFrame(housing_CV.cv_results_).sort_values(by=["rank_test_score"])

# make predictions with test data
housing_preds = housing_CV.predict(housing_test.drop(columns="price"))
print(mean_squared_error(housing_test["price"], housing_preds, squared=False))