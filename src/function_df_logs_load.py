<<<<<<< HEAD

import pandas as pd

def clean_df_logs(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure client_id is treated as string
    df['client_id'] = df['client_id'].astype(str)

    # Convert date_time to datetime format
    df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')

    # Drop duplicate rows
    df = df.drop_duplicates()

=======

import pandas as pd

def clean_df_logs(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure client_id is treated as string
    df['client_id'] = df['client_id'].astype(str)

    # Convert date_time to datetime format
    df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')

    # Drop duplicate rows
    df = df.drop_duplicates()

>>>>>>> b22304e96210882adf1244408d163e0c5c903491
    return df