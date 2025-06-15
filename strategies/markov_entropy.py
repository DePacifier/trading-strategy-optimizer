import pandas as pd
import numpy as np
from .base_strategy import Strategy
from utils.enums import TradeAction
from utils.markov_entropy import rolling_markov, calendar_bucket


class MarkovEntropyStrategy(Strategy):
    def __init__(
        self,
        lookback_days,
        edge_threshold,
        entropy_threshold,
        stationary_threshold,
        kl_threshold,
        bucket_level="4h",
        stop_loss_pct=1,
        take_profit_pct=1,
        label_scheme="fixed",
    ):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.lookback_days = int(lookback_days)
        self.edge_threshold = float(edge_threshold)
        self.entropy_threshold = float(entropy_threshold)
        self.bucket_level = bucket_level
        self.label_scheme = label_scheme
        self.stationary_threshold = float(stationary_threshold)
        self.kl_threshold = float(kl_threshold)

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        metrics = rolling_markov(
            data,
            bucket_level=self.bucket_level,
            window_days=self.lookback_days,
            label_scheme=self.label_scheme,
        )
        if not metrics:
            return pd.Series(TradeAction.EXIT.value, index=data.index)

        latest_date = max(metrics)
        current_bucket = calendar_bucket(
            pd.DatetimeIndex([latest_date]), self.bucket_level
        )[0]
        m = metrics.get(latest_date, {}).get(current_bucket)
        if m is None:
            return pd.Series(TradeAction.EXIT.value, index=data.index)

        edge = m["edge_vector"]
        entropy_rate = m["entropy_rate"]
        stationary = m["stationary"]
        kl = m["kl_div"]

        returns = np.log(data["close"]).diff()
        current_ret = returns.iloc[-1]
        current_label = pd.cut(
            [current_ret], bins=m["bin_edges"], labels=False, right=False
        )[0]

        long_cond = (
            edge.loc[current_label] > self.edge_threshold
            and entropy_rate < self.entropy_threshold
            and stationary.loc[current_label] > self.stationary_threshold
            and (
                pd.isna(kl.loc[current_label])
                or kl.loc[current_label] < self.kl_threshold
            )
        )

        short_cond = (
            edge.loc[current_label] < -self.edge_threshold
            and entropy_rate < self.entropy_threshold
            and stationary.loc[current_label] > self.stationary_threshold
            and (
                pd.isna(kl.loc[current_label])
                or kl.loc[current_label] < self.kl_threshold
            )
        )

        if long_cond:
            signal = TradeAction.ENTER_LONG.value
        elif short_cond:
            signal = TradeAction.ENTER_SHORT.value
        else:
            signal = TradeAction.EXIT.value

        return pd.Series(signal, index=data.index)
