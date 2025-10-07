<<<<<<< HEAD
import pandas as pd

def load_and_clean_df_clients(filepath: str) -> pd.DataFrame:
    # Load raw data
    df = pd.read_csv(filepath, sep=',')

    # Rename columns for clarity
    df.rename(columns={
        'clnt_tenure_yr': 'client_tenure_years',
        'clnt_tenure_mnth': 'client_tenure_months',
        'clnt_age': 'age',
        'gendr': 'gender',
        'num_accts': 'number_of_accounts',
        'bal': 'balance',
        'calls_6_mnth': 'calls_6_months',
        'logons_6_mnth': 'logons_6_months'
    }, inplace=True)

    # Ensure client_id is string
    df['client_id'] = df['client_id'].astype(str)

    # Fill numerical NaNs with column medians
    num_cols = df.select_dtypes(include='number').columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    # Fill gender NaNs with mode and normalize 'X' to 'U'
    if 'gender' in df.columns:
        df['gender'] = df['gender'].fillna(df['gender'].mode()[0])
        df['gender'] = df['gender'].replace('X', 'U')

    # Cast selected columns to integer
    df = df.astype({
        'client_tenure_years': 'int64',
        'client_tenure_months': 'int64',
        'number_of_accounts': 'int64',
        'calls_6_months': 'int64',
        'logons_6_months': 'int64'
    })

=======
import pandas as pd

def load_and_clean_df_clients(filepath: str) -> pd.DataFrame:
    # Load raw data
    df = pd.read_csv(filepath, sep=',')

    # Rename columns for clarity
    df.rename(columns={
        'clnt_tenure_yr': 'client_tenure_years',
        'clnt_tenure_mnth': 'client_tenure_months',
        'clnt_age': 'age',
        'gendr': 'gender',
        'num_accts': 'number_of_accounts',
        'bal': 'balance',
        'calls_6_mnth': 'calls_6_months',
        'logons_6_mnth': 'logons_6_months'
    }, inplace=True)

    # Ensure client_id is string
    df['client_id'] = df['client_id'].astype(str)

    # Fill numerical NaNs with column medians
    num_cols = df.select_dtypes(include='number').columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    # Fill gender NaNs with mode and normalize 'X' to 'U'
    if 'gender' in df.columns:
        df['gender'] = df['gender'].fillna(df['gender'].mode()[0])
        df['gender'] = df['gender'].replace('X', 'U')

    # Cast selected columns to integer
    df = df.astype({
        'client_tenure_years': 'int64',
        'client_tenure_months': 'int64',
        'number_of_accounts': 'int64',
        'calls_6_months': 'int64',
        'logons_6_months': 'int64'
    })

>>>>>>> b22304e96210882adf1244408d163e0c5c903491
    return df  # This is df_clients