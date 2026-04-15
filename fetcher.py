from dotenv import load_dotenv
import os
from newsapi import NewsApiClient
from datetime import datetime, timedelta

load_dotenv()
key = os.getenv('NEWS_API_KEY')
client = NewsApiClient(api_key=key) 

def fetch_articles(ticker):

    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    response = client.get_everything(q=ticker, language='en', sort_by='publishedAt', page_size=20, from_param=from_date)
    return [
            {
                'ticker': ticker,
                'title': article['title'],
                'description': article['description'],
                'published_at': article['publishedAt'],
                'source': article['source']['name'],
                'url': article['url']
            }
            for article in response['articles']
        ]
