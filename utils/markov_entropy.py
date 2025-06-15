import pandas as pd
import numpy as np
from typing import Iterable, List, Literal, Tuple, Dict
from scipy.stats import entropy


def _fixed_bins() -> List[float]:
    return [-np.inf, -0.05, -0.02, -0.005, 0.005, 0.02, 0.05, np.inf]


def _vol_scaled_bins(returns: pd.Series, mults: Iterable[float] = (-3, -2, -1, 1, 2, 3)) -> List[float]:
    sig = returns.std(ddof=0)
    if np.isnan(sig) or sig == 0:
        raise ValueError("Volatility is zero – cannot build vol-scaled bins.")
    edges = [-np.inf] + [m * sig for m in mults] + [np.inf]
    return sorted(edges)


def _quantile_bins(
    returns: pd.Series,
    quantiles: Iterable[float] = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99),
) -> List[float]:
    qs = returns.quantile(list(quantiles)).to_list()
    return [-np.inf] + qs + [np.inf]


def choose_magnitude_bins(
    returns: pd.Series,
    scheme: Literal["fixed", "vol", "quantile"] = "fixed",
    *,
    mults: Iterable[float] | None = None,
    quantiles: Iterable[float] | None = None,
) -> List[float]:
    if scheme == "fixed":
        return _fixed_bins()
    elif scheme == "vol":
        return _vol_scaled_bins(returns, mults or (-3, -2, -1, 1, 2, 3))
    elif scheme == "quantile":
        return _quantile_bins(returns, quantiles or (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99))
    else:
        raise ValueError(f"Unknown bin scheme: {scheme}")


def label_returns(
    closes: pd.Series,
    scheme: Literal["fixed", "vol", "quantile"] = "fixed",
    lookback: int | None = None,
    **kwargs,
) -> Tuple[pd.Series, List[float]]:
    log_ret = np.log(closes).diff()
    calib_slice = log_ret.dropna() if lookback is None else log_ret.dropna().iloc[-lookback:]
    edges = choose_magnitude_bins(calib_slice, scheme, **kwargs)
    labels = pd.cut(log_ret, bins=edges, labels=False, right=False)
    return labels, edges


def calendar_bucket(
    index: pd.DatetimeIndex,
    level: Literal["week", "weekday", "hour", "4h", "session"] = "weekday",
) -> pd.Index:
    if level == "week":
        return index.isocalendar().week.astype(int)
    if level == "weekday":
        return index.weekday
    if level == "hour":
        return index.hour
    if level == "4h":
        return (index.hour // 4)
    if level == "session":
        h = index.hour
        labels = np.select(
            [
                (h >= 0) & (h < 7),
                (h >= 7) & (h < 13),
                (h >= 13) & (h < 20),
                (h >= 20) & (h < 24),
            ],
            ["AS", "EU", "US", "AS"],
            default="AS",
        )
        return pd.Series(labels, index=index)
    raise ValueError(level)


def markov_chain_metrics(
    label_series: pd.Series,
    bin_edges: list,
    up_bins=None,
    down_bins=None,
    prev_matrix=None,
) -> Dict[str, object]:
    k = len(bin_edges) - 1
    all_states = list(range(k))
    up_bins = up_bins if up_bins is not None else [i for i in range(k) if i >= k // 2 + 1]
    down_bins = down_bins if down_bins is not None else [i for i in range(k) if i <= k // 2 - 1]

    src = label_series.shift(1).dropna()
    dst = label_series.loc[src.index]
    counts = pd.crosstab(src, dst)
    counts = counts.reindex(index=all_states, columns=all_states, fill_value=0)
    matrix = counts.div(counts.sum(axis=1), axis=0).fillna(0)

    eigvals, eigvecs = np.linalg.eig(matrix.T)
    ix = np.isclose(eigvals, 1)
    if np.any(ix):
        stationary = np.real(eigvecs[:, ix][:, 0])
        stationary /= stationary.sum()
        stationary = pd.Series(stationary, index=matrix.index)
    else:
        k = len(matrix)
        stationary = pd.Series([1 / k] * k, index=matrix.index)

    entropy_rate = sum(
        stationary.get(i, 0) * entropy(matrix.loc[i], base=2)
        if matrix.loc[i].sum() > 0 else 0
        for i in matrix.index
    )
    non_triv = [e for e in np.real(eigvals) if not np.isclose(e, 1)]
    spectral_gap = 1 - abs(max(non_triv, default=0))
    self_persist = np.mean(np.diag(matrix.to_numpy()))
    edge_vec = matrix[up_bins].sum(axis=1) - matrix[down_bins].sum(axis=1)

    if prev_matrix is not None:
        aligned_prev = prev_matrix.reindex_like(matrix).fillna(0)
        frob = np.linalg.norm(matrix.to_numpy() - aligned_prev.to_numpy())
        kl = matrix.apply(
            lambda row: entropy(row, aligned_prev.loc[row.name], base=2)
            if row.name in aligned_prev.index and row.sum() > 0 and aligned_prev.loc[row.name].sum() > 0
            else np.nan,
            axis=1,
        )
    else:
        frob, kl = np.nan, pd.Series(np.nan, index=matrix.index)

    return {
        "P": matrix,
        "counts": counts,
        "stationary": stationary,
        "entropy_rate": entropy_rate,
        "spectral_gap": spectral_gap,
        "self_stay": self_persist,
        "edge_vector": edge_vec,
        "frobenius": frob,
        "kl_div": kl,
        "bin_edges": bin_edges,
    }


def rolling_markov(
    df: pd.DataFrame,
    bucket_level: str = "weekday",
    window_days: int = 90,
    label_scheme: str = "fixed",
    **label_kwargs,
) -> Dict[pd.Timestamp, Dict[object, Dict[str, object]]]:
    closes = df["close"].copy()
    stride = 1
    results: Dict[pd.Timestamp, Dict[object, Dict[str, object]]] = {}
    prev_matrix = None
    date_range = closes.index.normalize().unique()[window_days::stride]

    for as_of in date_range:
        window_start = as_of - pd.Timedelta(days=window_days)
        sub = closes.loc[window_start:as_of]
        labels, bin_edges = label_returns(sub, scheme=label_scheme, lookback=None, **label_kwargs)
        key = calendar_bucket(labels.index, bucket_level)
        joined = pd.DataFrame({"label": labels, "bucket": key}).dropna()

        for b in joined["bucket"].unique():
            sub_labels = joined.loc[joined["bucket"] == b, "label"]
            if len(sub_labels) < 10:
                continue
            metrics = markov_chain_metrics(sub_labels, bin_edges, prev_matrix=prev_matrix)
            results.setdefault(as_of, {})[b] = metrics
            prev_matrix = metrics["P"]
    return results
