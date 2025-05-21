import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import logging

# Custom MAPE function (since sklearn does not have it directly)
def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------- Preprocessing Functions ----------

def get_features_and_target(df, feature_keyword='features', target_keyword='target'):
    features = [col for col in df.columns if feature_keyword in col]
    target = [col for col in df.columns if target_keyword in col]
    return features, target

def clean_features(features, df, useless_list, to_remove_dict):
    # Remove features with missing values
    features = [col for col in features if df[col].isna().sum() == 0]
    # Remove features identified as "useless"
    features = [col for col in features if col not in useless_list]
    # Remove additional features from dictionary keys
    for key in to_remove_dict:
        for col in to_remove_dict[key]:
            if col in features:
                features.remove(col)
    return features

def prepare_features(base_features, df, useless_list, feature_dict, include_keys=None):
    """
    Clean base features and add optional subsets from feature_dict.

    :param base_features: List of initial features (e.g. all columns with 'features' in name)
    :param df: The dataframe.
    :param useless_list: List of useless feature names to remove.
    :param feature_dict: Dictionary where each key is a feature subset name and value is a list of feature names.
    :param include_keys: List of keys from feature_dict to add to base features (e.g., ['adv', 'scouting_reports']).
    :return: Tuple -> (final feature list, list of included feature types)
    """
    # 1. Remove features with missing values
    features = [col for col in base_features if df[col].isna().sum() == 0]

    # 2. Remove known useless features
    features = [col for col in features if col not in useless_list]

    # 3. Remove all features listed in the dict
    for subset in feature_dict.values():
        features = [col for col in features if col not in subset]

    # 4. Optionally re-include selected subsets
    included_types = []
    if include_keys:
        for key in include_keys:
            for feat in feature_dict.get(key, []):
                if feat in df.columns and feat not in features and df[feat].isna().sum() == 0:
                    features.append(feat)
            included_types.append(key)

    return features, included_types

# ---------- Model Evaluation Function ----------
def db_select(df, drop_cols=None, index_col='Player_features'):
    df = df.copy()
    df.set_index(index_col, inplace=True)
    if drop_cols is None:
        drop_cols = []

    return df

# ---------- Model Evaluation Function ----------

def evaluate_models(df, features, metric='WS/48', season_range=range(1, 11), 
                    index_col='Player_features', drop_cols=None,
                    models_dict=None, scalers_dict=None, test_sizes=None, feature_types=None):
    """
    Evaluate different models with different scaler options and test sizes.
    
    :param df: DataFrame containing your data.
    :param features: List of features to be used.
    :param metric: The metric prefix in your target column naming.
    :param season_range: Range for target seasons.
    :param index_col: Column to set as DataFrame index.
    :param drop_cols: Columns to drop (e.g., features that need to be removed).
    :param models_dict: Dictionary of models to test; keys are model names, values are estimator instances.
    :param scalers_dict: Dictionary of scaler instances to test; keys are scaler names.
    :param test_sizes: List of test sizes (floats) to experiment with.
    :return: DataFrame summarizing evaluation results.
    """
    if drop_cols is None:
        drop_cols = []
    if models_dict is None:
        models_dict = {
            "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42, max_depth=3)
        }
    if scalers_dict is None:
        scalers_dict = {
            "StandardScaler": StandardScaler(),
            "MinMaxScaler": MinMaxScaler(),
            "Normalizer": Normalizer()
        }
    if test_sizes is None:
        test_sizes = [0.2]
        # Evaluate

    # Make a copy and set index
    df_model = df.copy()
    df_model.set_index(index_col, inplace=True)
    
    # DataFrame to collect results
    results_df = pd.DataFrame(columns=[
    'Target', 'Model', 'Scaler', 'Test_Size', 'Feature_Types', 'MSE', 'MAE', 'MAPE', 'R2', 'Rows', 'Columns'])
    
    for test_size in test_sizes:
        for scaler_name, scaler in scalers_dict.items():
            for model_name, model in models_dict.items():
                logging.info(f"Evaluating Model: {model_name}, Scaler: {scaler_name}, Test Size: {test_size}")
                # Evaluate for each season target
                for season in season_range:
                    target_name = f'{metric}-{season}_target'
                    # Filter indices for non-null target values
                    indices = df_model[df_model[target_name].notnull()].index
                    X = df_model.loc[indices, features].drop(columns=drop_cols, errors='ignore')
                    y = df_model.loc[indices, target_name]
    
                    # Split the data
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                        random_state=42, shuffle=True)
    
                    # Build a pipeline with the scaler and the model
                    pipeline = Pipeline([
                        ('scaler', scaler),
                        ('estimator', model)
                    ])
                    pipeline.fit(X_train, y_train)
                    
                    # Predictions and evaluation
                    y_train_pred = pipeline.predict(X_train)
                    y_test_pred = pipeline.predict(X_test)
                    r2 = r2_score(y_test, y_test_pred)
                    mse = mean_squared_error(y_test, y_test_pred)
                    mae = mean_absolute_error(y_test, y_test_pred)
                    mape = mean_absolute_percentage_error(y_test, y_test_pred)
                    
                    # Append results
                    temp_dict = {
                    'Target': target_name,
                    'Model': model_name,
                    'Scaler': scaler_name,
                    'Test_Size': test_size,
                    'Feature_Types': ', '.join(feature_types) if feature_types else 'base',
                    'MSE': mse,
                    'MAE': mae,
                    'MAPE': mape,
                    'R2' : r2,
                    'Columns': X.shape[1],
                    'Rows' : X.shape[0]
                    }

                    results_df = pd.concat([results_df, pd.DataFrame([temp_dict])], ignore_index=True)
                    
                    logging.info(f"Target: {target_name} | MSE: {mse:.3f} | MAE: {mae:.3f} | "
                                 f"Test R²: {r2:.3f} | MAPE: {mape:.3f}")
    
    return results_df

