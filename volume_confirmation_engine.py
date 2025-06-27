import pandas as pd
import numpy as np

class VolumeConfirmationEngine:
    def __init__(self, short_term_minutes=5, long_term_minutes=30, zscore_window=20):
        self.short_term_minutes = short_term_minutes
        self.long_term_minutes = long_term_minutes
        self.zscore_window = zscore_window

    def calculate_zscore(self, series):
        rolling_mean = series.rolling(window=self.zscore_window).mean()
        rolling_std = series.rolling(window=self.zscore_window).std()
        zscore = (series - rolling_mean) / (rolling_std + 1e-9)
        return zscore

    def get_volume_ratio(self, df, short_window, long_window):
        short_volume = df['volume'].rolling(window=short_window).sum()
        long_volume = df['volume'].rolling(window=long_window).sum()
        volume_ratio = short_volume / (long_volume + 1e-9)
        return volume_ratio

    def detect_breakout(self, df, threshold=1.2):
        short_term = df['price'].rolling(window=self.short_term_minutes).mean()
        long_term = df['price'].rolling(window=self.long_term_minutes).mean()
        breakout = (short_term > long_term * threshold).astype(int)
        return breakout

    def run_analysis(self, df):
        """
        Expects df with columns: 'timestamp', 'price', 'volume'
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # ✅ Use '1min' instead of deprecated '1T'
        df = df.resample('1min').agg({'price': 'last', 'volume': 'sum'}).dropna()

        df['volume_zscore'] = self.calculate_zscore(df['volume'])
        df['volume_ratio'] = self.get_volume_ratio(df, self.short_term_minutes, self.long_term_minutes)
        df['breakout'] = self.detect_breakout(df)
        df['score'] = df['volume_zscore'] * df['volume_ratio']

        return df[['price', 'volume', 'volume_zscore', 'volume_ratio', 'breakout', 'score']]

# 🧪 Local test
if __name__ == "__main__":
    from datetime import datetime, timedelta

    timestamps = pd.date_range(end=datetime.now(), periods=60, freq='1min')
    prices = np.linspace(100, 130, 60) + np.random.normal(0, 1, 60)
    volumes = np.random.randint(1000, 3000, size=60)

    test_df = pd.DataFrame({
        'timestamp': timestamps,
        'price': prices,
        'volume': volumes,
    })

    engine = VolumeConfirmationEngine()
    result = engine.run_analysis(test_df)

    print(result.tail(10))