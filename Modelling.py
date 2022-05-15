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
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error


housing_data = pd.read_excel("data/housing_data_prepped.xlsx", index_col=0, decimal = ",")

# train and test split
housing_train, housing_test = train_test_split(housing_data,
                                               test_size=0.2,
                                               random_state=3)

# Random Forest with Cross Validation
housing_DT = RandomForestRegressor(random_state=3)
housing_params = {"min_samples_split": [2, 3, 3, 4],
                  "max_features": [4, 5, 6, 7, 8],
                  "max_samples": [0.5, 0.6, 0.7,  0.8],
                  "max_depth": [14, 16, 18, 20]}

housing_CV = GridSearchCV(housing_DT, housing_params, cv = 3)

# create fit
housing_CV.fit(housing_train.drop(columns="price"), housing_train["price"])
housing_CV_res = pd.DataFrame(housing_CV.cv_results_).sort_values(by=["rank_test_score"])

# feature importance
housing_importance = pd.DataFrame({"variables": housing_data.drop(columns="price").columns,
                                   "FI": housing_CV.best_estimator_.feature_importances_})

housing_importance = housing_importance.sort_values("FI", ascending=False).reset_index()

sns.barplot(x="variables", y="FI", data= housing_importance)
for index, value in enumerate(housing_importance.FI):
    plt.text(index, value,
             str(round(value, 2)), ha="center")
plt.xlabel("variables")
plt.ylabel("Feature Importance")
plt.title(f'Feature Importance Housing')
plt.tight_layout()

# make predictions with test data
housing_preds = housing_CV.predict(housing_test.drop(columns="price"))
print(mean_squared_error(housing_test["price"], housing_preds, squared=False))
print(mean_absolute_error(housing_test["price"], housing_preds))

# Analyse predictions
plt.scatter(housing_test["price"], housing_preds)
plt.plot([housing_test["price"].min(), housing_test["price"].max()],
         [housing_test["price"].min(), housing_test["price"].max()], "k--", lw=4)
plt.xlabel('Price')
plt.ylabel('Predicted price')
plt.title("Actual price vs. predicted price")
plt.show()

housing_test.insert(1, "preds", housing_preds)
housing_data.head()