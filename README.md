# FinSentiment

A real-time financial news sentiment dashboard powered by FinBERT, a domain-specific transformer model fine-tuned on financial text. FinSentiment pulls live news articles, runs sentiment inference, and correlates results with stock price movements, giving you a data-driven view of how the market narrative aligns with price action.

---

## Features

- **Live News Ingestion:** Fetches recent financial news via NewsAPI, filtered by stock ticker
- **FinBERT Sentiment Analysis:** Classifies each article as positive, negative, or neutral using ProsusAI/finbert, a BERT model fine-tuned specifically on financial language
- **Stock Price Overlay:** Pulls live OHLCV data via yFinance and overlays it with daily average sentiment on a dual-axis chart
- **Sentiment-Price Correlation:** Computes Pearson correlation between sentiment momentum and next-day price returns
- **Backtesting:** Simulates a sentiment-driven trading strategy against buy-and-hold, with cumulative return comparison
- **Sentiment Distribution:** Donut chart showing the proportion of positive, negative, and neutral coverage per ticker
- **Word Cloud:** Generated from article headlines, sized by frequency
- **Article Drill Down:** Select any date to see the specific articles that drove that day's sentiment
- **Multi-Ticker Support:** Analyze multiple tickers simultaneously in a single run
- **Negative Sentiment Alert:** Flags tickers with dominant negative sentiment and low confidence scores
- **CSV Export:** Download the full articles and sentiment scores table
- **Persistent Storage:** SQLite database caches articles and sentiment scores to avoid redundant API and inference calls

---

## Tech Stack

| Layer | Technology |
|---|---|
| NLP Model | FinBERT (HuggingFace Transformers) |
| News Data | NewsAPI |
| Stock Data | yFinance |
| Storage | SQLite |
| Visualisation | Plotly |
| Frontend | Streamlit |
| Language | Python 3.10+ |

---

## Project Structure
finsentiment/
├── app.py               Main Streamlit application and UI
├── fetcher.py           NewsAPI integration, fetches articles by ticker
├── sentiment.py         FinBERT inference, returns label and confidence score
├── stocks.py            yFinance wrapper, returns daily close prices
├── database.py          SQLite schema, article and sentiment read/write
├── correlation.py       Pearson correlation, sentiment vs next-day returns
├── backtest.py          Sentiment momentum strategy vs buy-and-hold
├── wordcloud_gen.py     Word cloud from article headlines
├── requirements.txt     Python dependencies
├── .env                 API keys, not committed
└── .gitignore
