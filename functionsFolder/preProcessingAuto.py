import pandas as pd
import numpy as np
import re
import nltk
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler, Normalizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to log the shape of the dataframe at various steps
def log_shape(df, step):
    logging.info(f"After {step}: shape = {df.shape}")

# Download required NLTK resources (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# --------------------------------------------
# 1. Dummy Variable Creation
# --------------------------------------------
def create_dummy_variables(df):
    """Create dummy variables based on whether a field is NaN."""
    logging.info("Creating dummy variables...")
    df['dummy_hs_ranking_features'] = df['RSCI Top 100_features'].apply(lambda x: 0 if pd.isna(x) else 1)
    df['dummy_coll_awards_features'] = df['average_Awards_features'].apply(lambda x: 0 if pd.isna(x) else 1)
    df['dummy_mock_draft_features'] = df['Draft_pos_features'].apply(lambda x: 0 if pd.isna(x) else 1)
    df['dummy_scouting_reports_features'] = df['Strength_features'].apply(lambda x: 0 if pd.isna(x) else 1)
    log_shape(df, "dummy variable creation")
    return df

# --------------------------------------------
# 2. Categorization and One-Hot Encoding
# --------------------------------------------
def categorize_ranking(row):
    """Return a categorical rank from a string or mark as 'Not in the classement'."""
    if pd.isna(row) or row == 'NaN':
        return 'Not in the classement'
    else:
        try:
            rank = int(row.split()[0])
        except:
            rank = row
        if 1 <= rank <= 25:
            return '1-25'
        elif 26 <= rank <= 50:
            return '26-50'
        elif 51 <= rank <= 75:
            return '51-75'
        elif 76 <= rank <= 100:
            return '76-100'
        else:
            return 'Not in the classement'

def categorize_and_encode(df, columns_to_categorize=None, other_categorical=None):
    """
    Categorize ranking features and one-hot encode selected categorical columns.
    
    :param df: Input dataframe.
    :param columns_to_categorize: Dict mapping new column names to original columns.
           Example: {'rsci': 'RSCI Top 100_features', 'mock_draft': 'Draft_pos_features'}.
    :param other_categorical: List of additional categorical columns to one-hot encode.
    :return: DataFrame with one-hot encoded columns added and original categorical columns dropped.
    """
    logging.info("Categorizing and one-hot encoding categorical features...")
    if columns_to_categorize is None:
        columns_to_categorize = {
            'rsci': 'RSCI Top 100_features',
            'mock_draft': 'Draft_pos_features'
        }
    for new_col, orig_col in columns_to_categorize.items():
        df[new_col] = df[orig_col].apply(categorize_ranking)
    
    if other_categorical is None:
        other_categorical = ['mock_draft', 'rsci', 'Pos_x_features', 'Class_features']
    
    encoder = OneHotEncoder(sparse_output=False)
    encoded_array = encoder.fit_transform(df[other_categorical])
    encoded_df = pd.DataFrame(encoded_array, 
                              columns=encoder.get_feature_names_out(other_categorical),
                              index=df.index)  # Preserve the index!
    encoded_df = encoded_df.add_suffix('_features')
    df = pd.concat([df, encoded_df], axis=1)
    df = df.drop(other_categorical, axis=1)
    log_shape(df, "categorization and one-hot encoding")
    return df

# --------------------------------------------
# 3. Unstructured Text Processing and Vectorization
# --------------------------------------------
def utils_preprocess_text(text, flg_stemm=False, flg_lemm=True, lst_stopwords=True):
    """Cleans text: lower-case, remove punctuation, tokenize, remove stopwords,
    plus optional stemming/lemmatization."""
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    lst_text = word_tokenize(text)
    
    if lst_stopwords is None:
        lst_stopwords = stopwords.words('english')
    lst_text = [word for word in lst_text if word not in lst_stopwords]
    
    if flg_stemm:
        ps = nltk.stem.PorterStemmer()
        lst_text = [ps.stem(word) for word in lst_text]
    if flg_lemm:
        lem = WordNetLemmatizer()
        lst_text = [lem.lemmatize(word) for word in lst_text]
    
    return " ".join(lst_text)

def process_unstructured_text(df, strength_col='Strength_features', weakness_col='Weakness_features',
                              text_col='clean_2', max_features=None, prefix='text_', suffix='_features'):
    """
    Combine text columns, clean text, and vectorize via TF-IDF.
    
    :param df: DataFrame containing text fields.
    :param strength_col: Name for strengths column.
    :param weakness_col: Name for weaknesses column.
    :param text_col: Name for the cleaned text column.
    :param max_features: Maximum number of TF-IDF features.
    :param prefix: Prefix for the output TF-IDF columns.
    :param suffix: Suffix for the output TF-IDF columns.
    :return: DataFrame of TF-IDF features with the same index as df.
    """
    logging.info("Processing unstructured text data...")
    # Copy the relevant columns and preserve the index
    unstructured = df[['player_id', strength_col, weakness_col]].copy()
    # Create combined text and flag
    unstructured['text'] = unstructured[strength_col].fillna('') + " " + unstructured[weakness_col].fillna('')
    unstructured['flag_reports_features'] = unstructured['text'].apply(
        lambda x: 0 if x.strip() == '' else 1
    )
    unstructured['text'] = unstructured['text'].replace(r'^\s*$', 'No scouting report available', regex=True)

    unstructured['text'] = unstructured[strength_col].fillna('') + " " + unstructured[weakness_col].fillna('')
    unstructured['text'] = unstructured['text'].replace(r'^\s*$', 'No scouting report available', regex=True)
    
    lst_stop = stopwords.words("english")
    unstructured[text_col] = unstructured['text'].apply(lambda x: utils_preprocess_text(x, flg_stemm=False, flg_lemm=True, lst_stopwords=lst_stop))
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=max_features, ngram_range=(1, 1))
    X_tfidf = vectorizer.fit_transform(unstructured[text_col])
    tfidf_df = pd.DataFrame(X_tfidf.toarray(), 
                            columns=vectorizer.get_feature_names_out(),
                            index=unstructured.index)  # Preserve index here!
    tfidf_df = tfidf_df.add_prefix(prefix).add_suffix(suffix)
    tfidf_df['flag_reports_features'] = unstructured['flag_reports_features']
    log_shape(tfidf_df, "TF-IDF vectorization")
    return tfidf_df

# --------------------------------------------
# 4. Imputation for Opponent Columns
# --------------------------------------------
def impute_opponent_columns(df, opp_columns, team_col='Team_features', season_col='season_features',
                            missing_years=(2006, 2009), proxy_years=(2010, 2025)):
    """
    Impute missing opponent columns based on team medians within proxy seasons.
    """
    logging.info("Imputing opponent columns based on team data...")
    for team in df[team_col].unique():
        team_mask = df[team_col] == team
        proxy_mask = team_mask & df[season_col].between(proxy_years[0], proxy_years[1])
        proxy_medians = df.loc[proxy_mask, opp_columns].median()
        missing_mask = team_mask & df[season_col].between(missing_years[0], missing_years[1])
        df.loc[missing_mask, opp_columns] = df.loc[missing_mask, opp_columns].fillna(proxy_medians)
    log_shape(df, "imputation using team data")
    return df

def impute_opponent_from_recovery(df, opp_columns, recovery_file, school_col='School_features', season_col='season_features',
                                  missing_years=(2006, 2009), proxy_years=(2010, 2025)):
    """
    Impute missing opponent columns from a recovery file based on school medians.
    """
    logging.info("Imputing opponent columns using recovery data...")
    recovery_df = pd.read_excel(recovery_file)
    recovery_df = recovery_df.add_suffix('_features')
    
    for team in df[school_col].unique():
        team_mask = recovery_df[school_col] == team
        proxy_mask = team_mask & recovery_df[season_col].between(proxy_years[0], proxy_years[1])
        proxy_medians = recovery_df.loc[proxy_mask, opp_columns].median()
        missing_mask = team_mask & df[season_col].between(missing_years[0], missing_years[1])
        df.loc[missing_mask, opp_columns] = df.loc[missing_mask, opp_columns].fillna(proxy_medians)
    log_shape(df, "imputation using recovery data")
    return df

# --------------------------------------------
# 5. Final Adjustments and Cleanup
# --------------------------------------------
def fill_and_cleanup(df, stats, additional_fill_cols=None, drop_cond_cols=None):
    """
    Fill missing values for stats columns and drop rows where critical columns are missing.
    
    :param df: DataFrame to process.
    :param stats: List of prefixes (e.g., ['average', 'per_40', 'totals']) for columns to fill.
    :param additional_fill_cols: Optional list of other columns to fill.
    :param drop_cond_cols: List of columns where NaN indicates row to drop.
    :return: Cleaned DataFrame.
    """
    logging.info("Filling missing values and cleaning up the dataframe...")
    for stat in stats:
        col_name = f'{stat}_3P%_features'
        if col_name in df.columns:
            df[col_name] = df[col_name].fillna(0)
    if additional_fill_cols:
        for col in additional_fill_cols:
            df[col] = df[col].fillna(0)
    if drop_cond_cols:
        drop_mask = df[drop_cond_cols].isnull().any(axis=1)
        df = df[~drop_mask]
    log_shape(df, "final cleanup")
    return df

# --------------------------------------------
# 6. Main Preprocessing Function
# --------------------------------------------
def preprocess_working_df(df, recovery_file):
    """
    Run the full preprocessing pipeline on the working dataframe.
    
    :param df: The raw input dataframe.
    :param recovery_file: Path to the recovery excel file for opponent data imputation.
    :return: Processed dataframe.
    """
    logging.info("Starting full preprocessing pipeline...")
    
    # Step 1: Dummy variables
    df = create_dummy_variables(df)
    
    # Step 2: Categorize and one-hot encode categorical features
    df = categorize_and_encode(df)
    
    # Step 3: Process unstructured text and merge TF-IDF features
    tfidf_df = process_unstructured_text(df)
    df = pd.concat([df, tfidf_df], axis=1)
    log_shape(df, "after TF-IDF merge")
    
    # Step 4: Impute opponent columns using team data
    opp_columns = [col for col in df.columns if '_opp' in col and 'text' not in col]
    df = impute_opponent_columns(df, opp_columns)
    
    # Step 4b: Impute opponent columns using recovery data
    df = impute_opponent_from_recovery(df, opp_columns, recovery_file)
    
    # Step 5: Fill missing stats and drop rows with critical missing values
    stats = ['average', 'per_40', 'totals']
    drop_cond_cols = ['average_FTA_features', 'TRB_opp_features']
    df = fill_and_cleanup(df, stats, drop_cond_cols=drop_cond_cols)
    
    # Optionally, drop additional columns if needed:
    # df = df.drop('MP_team_features', axis=1)
    
    logging.info("Preprocessing complete!")
    log_shape(df, "final output")
    return df