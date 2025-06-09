import sqlite3
from typing import Iterable

from strategy_manager import Trade

class TradeRecorder:
    """Persist trades to a SQLite database."""

    def __init__(self, db_path: str = "trades.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        self._recorded = set()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trades(
                entry_time TEXT PRIMARY KEY,
                entry_price REAL,
                position INTEGER,
                exit_time TEXT,
                exit_price REAL,
                profit_loss REAL,
                stop_loss REAL,
                take_profit REAL,
                size REAL,
                remaining_capital REAL
            )
            """
        )
        self.conn.commit()

    def sync(self, trades: Iterable[Trade]) -> None:
        """Sync the given trades with the database."""
        for trade in trades:
            key = trade.entry_time
            if key not in self._recorded:
                self._insert_trade(trade)
                self._recorded.add(key)
            elif trade.exit_time is not None:
                self._update_trade(trade)

    def _insert_trade(self, trade: Trade) -> None:
        data = trade.get_data()
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO trades(
                entry_time, entry_price, position,
                exit_time, exit_price, profit_loss,
                stop_loss, take_profit, size,
                remaining_capital
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                data["entry_time"],
                data["entry_price"],
                data["position"],
                data["exit_time"],
                data["exit_price"],
                data["profit_loss"],
                data["stop_loss"],
                data["take_profit"],
                data["size"],
                data["remaining_capital"],
            ),
        )
        self.conn.commit()

    def _update_trade(self, trade: Trade) -> None:
        data = trade.get_data()
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE trades SET
                exit_time=?,
                exit_price=?,
                profit_loss=?,
                remaining_capital=?
            WHERE entry_time=?
            """,
            (
                data["exit_time"],
                data["exit_price"],
                data["profit_loss"],
                data["remaining_capital"],
                data["entry_time"],
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

