import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score

from src.api import OilPriceAPI

from src.utils.config_manager import ConfigManager

# Load the config file
config_manager = ConfigManager("configs/config.yaml")
config = config_manager.config


def get_data(tank_id: int) -> tuple:
    """Get the data corresponding to the tank_id."""
    data = pd.read_pickle("data/processed/final_data.pickle")
    data = data[data["Tank-ID"] == tank_id]
    y_train = data["Verbrauch"]
    X_train = data.drop("Verbrauch", axis=1)
    return X_train, y_train


def run_oil_consumption_forecasting(context_num, forcast_num, tank_id, degree=3):
    """Run the oil consumption forecasting. Return the dataframe with historical and forecasted data. Note for this concept the current date can only be the last available in the dataset since we do not have a database connection to access current data."""
    # Get necessary data as df
    X_train, y_train = get_data(tank_id)
    # Trim to the context_num and reshape
    X_train = X_train.iloc[-context_num:]
    y_train = y_train.iloc[-context_num:]
    y_index = y_train.index
    X_index = X_train.index

    # Train and predict
    print(config["models"]["oilConsumption"])
    if config["models"]["oilConsumption"] == "polyReg":
        pass
    elif config["models"]["oilConsumption"] == "rf":
        pass
    else:
        raise ValueError("Invalid model for oil consumption forecasting")

    # Concat y_train with forcasting data
    tmp_y_train = pd.DataFrame(y_train)
    tmp_y_train["flag"] = "train"

    new_dates = pd.date_range(start=y_index.index[-1] + pd.Timedelta(days=1), periods=10, freq="D")
    tmp_y_forcast = pd.DataFrame({"value": 1}, index=new_dates)
    tmp_y_forcast["flag"] = "forcast"

    df = pd.concat([tmp_y_train, tmp_y_forcast])

    return df


def run_oil_price_forecasting(context_num, forcast_num, tank_id):
    """Run the oil price forecasting. Return the dataframe with historical and forecasted data."""
    # Get PLZ
    X_train, y_train = get_data(tank_id)
    y_index = y_train.index
    plz = X_train["plz"].iloc[-1]
    # Get historical data
    end_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    start_date = (pd.Timestamp.now() - pd.DateOffset(days=context_num)).strftime("%Y-%m-%d")
    oilP_api = OilPriceAPI()
    oilP_df = oilP_api.get_heizoel(plz, start_date, end_date)
    # Train and predict
    # implement y_forcast
    # Concat y_train with forcasting data
    tmp_y_train = pd.DataFrame(y_train)
    tmp_y_train["flag"] = "train"

    new_dates = pd.date_range(start=y_index.index[-1] + pd.Timedelta(days=1), periods=10, freq="D")
    tmp_y_forcast = pd.DataFrame({"value": 1}, index=new_dates)
    tmp_y_forcast["flag"] = "forcast"

    df = pd.concat([tmp_y_train, tmp_y_forcast])

    return df


def get_cleaned_data(path="data/processed/data_one_day_clean.pickle") -> pd.DataFrame:
    df = pd.read_pickle(path)
    # correct outliers
    df.loc[df["Verbrauch"] > 0, "Verbrauch"] = 0.0
    # take absolute values
    df["Verbrauch"] = df["Verbrauch"].abs()
    # drop NaN values
    df = df.dropna()
    df = df[["Zeitstempel", "Verbrauch"]]

    return df


def fit_linear_model(df: pd.DataFrame, context: int = 90, degree: int = 3, forecast_days: int = 7):
    # Get newest -Days Tage
    y = df["Verbrauch"].iloc[-context:].values.reshape(-1, 1)
    X = np.arange(len(y)).reshape(-1, 1)
    dates = df["Zeitstempel"].iloc[-context:].values
    future_days = pd.date_range(start=dates.max() + pd.Timedelta(days=1), periods=forecast_days, freq="D")

    # Extend feature space to make polynomial regression
    poly = PolynomialFeatures(degree)
    X_poly = poly.fit_transform(X)

    # Fit linear regression with polynomial features
    lr = LinearRegression()
    lr.fit(X_poly, y)
    # Get best fitted line
    y_pred = lr.predict(X_poly)

    # Evaluate best fitted line
    r2 = r2_score(y_true=y, y_pred=y_pred)

    future_days_to_predict = np.arange(X.max(), X.max() + forecast_days).reshape(-1, 1)
    # Get prediction for future days
    future_days_extened = poly.transform(future_days_to_predict)
    y_pred_future = lr.predict(future_days_extened).flatten()

    y_train = pd.DataFrame({"Verbrauch": y.flatten(), "Zeitstempel": dates}, index=X.flatten())
    y_pred = pd.DataFrame({"Verbrauch": y_pred.flatten(), "Zeitstempel": dates}, index=X.flatten())
    y_pred_future = pd.DataFrame(
        {"Verbrauch": y_pred_future.flatten(), "Zeitstempel": future_days}, index=future_days_to_predict.flatten()
    )

    return y_train, y_pred, y_pred_future
