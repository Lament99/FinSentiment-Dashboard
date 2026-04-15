import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stocks_data(ticker, start_date):
    df = yf.download(ticker, start=start_date, end = datetime.now().strftime('%Y-%m-%d'))
    df.columns = df.columns.get_level_values(0)
    df = df[['Close']].reset_index()
    df.columns = ['Date', 'Close']
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df