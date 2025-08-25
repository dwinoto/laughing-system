from dataclasses import dataclass
import pandas as pd

@dataclass
class StrategyConfig:
    short_window: int = 20
    long_window: int = 50

class MovingAverageCrossover:
    """Simple moving average crossover strategy"""

    def __init__(self, config: StrategyConfig):
        self.config = config

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals.

        Args:
            data: DataFrame with 'close' prices column
        Returns:
            pd.Series of signals: 1 for buy, -1 for sell, 0 for hold
        """
        df = data.copy()
        df['sma_short'] = df['close'].rolling(window=self.config.short_window).mean()
        df['sma_long'] = df['close'].rolling(window=self.config.long_window).mean()
        signal = pd.Series(index=df.index, data=0)
        crossover_buy = (df['sma_short'] > df['sma_long']) & (df['sma_short'].shift(1) <= df['sma_long'].shift(1))
        crossover_sell = (df['sma_short'] < df['sma_long']) & (df['sma_short'].shift(1) >= df['sma_long'].shift(1))
        signal[crossover_buy] = 1
        signal[crossover_sell] = -1
        return signal