import pandas as pd
import numpy as np


class VolumeEngine:
    def __init__(self, historical_data: pd.DataFrame, baseline_window: int = 20):
        """
        Initialize the Volume Engine with historical market data.

        :param historical_data: DataFrame with at least a 'volume' column.
        :param baseline_window: Number of past days used to calculate the volume baseline.
        """
        if 'volume' not in historical_data.columns:
            raise ValueError("DataFrame must contain a 'volume' column.")

        self.data = historical_data.copy()
        self.baseline_window = baseline_window
        self.volume_baseline = None
        self.alerts = []

        self._calculate_volume_baseline()
        self._detect_unusual_volume()

    def _calculate_volume_baseline(self):
        """
        Calculate the rolling average of volume to serve as baseline.
        """
        self.data['volume_baseline'] = self.data['volume'].rolling(window=self.baseline_window).mean()
        self.volume_baseline = self.data['volume_baseline']

    def _detect_unusual_volume(self, threshold: float = 1.5):
        """
        Detect days where volume is significantly above baseline.

        :param threshold: Multiplier over baseline to define "unusual" volume.
        """
        self.data['is_unusual_volume'] = (
            (self.data['volume'] > self.data['volume_baseline'] * threshold)
        )
        self.alerts = self.data[self.data['is_unusual_volume']]

    def get_alerts(self) -> pd.DataFrame:
        """
        Get all detected unusual volume events.

        :return: DataFrame of unusual volume rows.
        """
        return self.alerts

    def get_processed_data(self) -> pd.DataFrame:
        """
        Return the original data with computed columns.

        :return: DataFrame including 'volume_baseline' and 'is_unusual_volume'.
        """
        return self.data


# Example Usage:
if __name__ == "__main__":
    # Load some historical volume data for testing
    sample_data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=60),
        'volume': np.random.randint(1000, 5000, size=60)
    })

    engine = VolumeEngine(sample_data)
    print("🚨 Unusual Volume Alerts:")
    print(engine.get_alerts())