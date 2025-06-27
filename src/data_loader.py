import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_data(self):
        try:
            df = pd.read_csv(self.filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp', 'price', 'volume']].dropna()
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return pd.DataFrame()