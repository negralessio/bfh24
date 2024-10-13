import pandas as pd

from src.api import OilPriceAPI

from utils.config_manager import ConfigManager

# Load the config file
config_manager = ConfigManager("../configs/config.yaml")
config = config_manager.config


def get_data(tank_id: int) -> tuple:
    """Get the data corresponding to the tank_id."""
    data = pd.read_pickle("../data/preprocessed/final_data.pickle")
    data = data[data["tank_id"] == tank_id]
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
    if config["models"]["oil_consumption"] == "polyReg":
        pass
    if config["models"]["oil_consumption"] == "rf":
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
