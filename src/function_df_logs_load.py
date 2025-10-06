
import pandas as pd

def clean_df_logs(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure client_id is treated as string
    df['client_id'] = df['client_id'].astype(str)

    # Convert date_time to datetime format
    df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')

    # Drop duplicate rows
    df = df.drop_duplicates()

    return df