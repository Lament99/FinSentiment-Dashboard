import pandas as pd

def run_backtest(daily_sentiment, stock_data, threshold=0.5):
    stock_data = stock_data.copy()
    stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.normalize()
    daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date']).dt.normalize()

    merged = pd.merge(stock_data, daily_sentiment, left_on='Date', right_on='date').sort_values('Date')
    if len(merged) < 2:
        return None

    merged['sentiment_change'] = merged['score'].diff()
    merged['signal'] = merged['sentiment_change'].apply(lambda x: 1 if x > 0 else -1)
    merged['market_return'] = merged['Close'].pct_change()
    merged['strategy_return'] = merged['signal'].shift(1) * merged['market_return']
    merged = merged.dropna()

    merged['cumulative_market'] = (1 + merged['market_return']).cumprod()
    merged['cumulative_strategy'] = (1 + merged['strategy_return']).cumprod()
    merged['Date'] = merged['Date'].astype(str)

    return merged[['Date', 'Close', 'signal', 'cumulative_market', 'cumulative_strategy']]