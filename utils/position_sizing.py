def risk_based_position_sizing(available_capital, risk_per_trade, entry_price, stop_loss_price):
    """Calculate position size based on risk per trade."""
    risk_amount = available_capital * risk_per_trade
    stop_loss_distance = abs(entry_price - stop_loss_price)
    position_size = risk_amount / stop_loss_distance
    max_position_size = available_capital / entry_price
    return min(position_size, max_position_size)

