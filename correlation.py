import pandas as pd

def calculate_correlation(daily_sentiment, stock_data):
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
    
    merged = pd.merge(stock_data, daily_sentiment, left_on='Date', right_on='date')
    merged['next_day_return'] = merged['Close'].pct_change().shift(-1)
    merged = merged.dropna()
    
    if len(merged) < 2:
        return None
    
    correlation = merged['score'].corr(merged['next_day_return'])
    return round(correlation, 2)