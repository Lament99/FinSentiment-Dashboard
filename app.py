import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import init_db, insert_article, insert_sentiment, get_articles_by_ticker
from fetcher import fetch_articles
from sentiment import analysis_sentiment
from stocks import get_stocks_data
from correlation import calculate_correlation
from backtest import run_backtest
from wordcloud_gen import render_wordcloud

st.set_page_config(page_title="FinSentiment", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', system-ui, sans-serif; }
.stApp { background-color: #080c10; }

[data-testid="stSidebar"] {
    background-color: #060910;
    border-right: 1px solid #141920;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #c8a96e;
    margin-bottom: 2px;
}

.sidebar-sub {
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #2a3040;
    margin-bottom: 24px;
}

.ticker-header {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: #e8e8e8;
    margin: 48px 0 2px 0;
    padding-bottom: 16px;
    border-bottom: 1px solid #141920;
}

.metric-card {
    background: #0c1018;
    border: 1px solid #141920;
    border-radius: 4px;
    padding: 22px 24px;
    position: relative;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 100%;
    background: #c8a96e;
    border-radius: 4px 0 0 4px;
    opacity: 0.4;
}

.metric-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #2e3a4a;
    margin-bottom: 12px;
    font-family: 'DM Mono', monospace;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #d4c5a9;
    letter-spacing: -0.02em;
    font-family: 'DM Mono', monospace;
}

.alert-negative {
    background: #0d0608;
    border-left: 2px solid #8b1a1a;
    padding: 14px 20px;
    border-radius: 2px;
    color: #8b1a1a;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 20px 0;
    font-family: 'DM Mono', monospace;
}

.section-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #2a3040;
    margin: 36px 0 14px 0;
    font-family: 'DM Mono', monospace;
}

.divider {
    border: none;
    border-top: 1px solid #0f141a;
    margin: 48px 0;
}

div[data-testid="stTextInput"] input {
    background-color: #0c1018;
    border: 1px solid #1a2030;
    color: #8a9bb0;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.05em;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #c8a96e;
    box-shadow: none;
}

div[data-testid="stTextInput"] label {
    color: #2e3a4a !important;
    font-size: 9px !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    font-family: 'DM Mono', monospace !important;
}

.stButton button {
    background-color: #c8a96e;
    color: #080c10;
    border: none;
    border-radius: 4px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 10px;
    width: 100%;
}

.stButton button:hover {
    background-color: #d4b87a;
    color: #080c10;
}

[data-testid="stDataFrame"] {
    border: 1px solid #141920;
    border-radius: 4px;
}

div[data-testid="stSelectbox"] label {
    display: none;
}
</style>
""", unsafe_allow_html=True)

init_db()

with st.sidebar:
    st.markdown('<div class="sidebar-title">FinSentiment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Market Intelligence</div>', unsafe_allow_html=True)
    tickers_input = st.text_input("Tickers", placeholder="AAPL, MSFT, TSLA")
    analyze = st.button("Run Analysis")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="color:#1a2030;font-size:10px;letter-spacing:0.15em;text-transform:uppercase;font-family:DM Mono,monospace;">FinBERT · NewsAPI · yFinance</p>', unsafe_allow_html=True)

tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if analyze:
    st.session_state['analyzed'] = True
    st.session_state['tickers'] = tickers

def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def color_sentiment(val):
    colors = {'positive': '#4a7c59', 'negative': '#8b1a1a', 'neutral': '#3a4a5a'}
    return f'color: {colors.get(val, "#d4c5a9")}'

CHART_LAYOUT = dict(
    paper_bgcolor='#080c10',
    plot_bgcolor='#080c10',
    font=dict(family='DM Mono, monospace', color='#2a3a4a', size=11),
    xaxis=dict(gridcolor='#0f141a', zeroline=False, showline=False, tickfont=dict(color='#2a3a4a')),
    yaxis=dict(gridcolor='#0f141a', zeroline=False, showline=False, tickfont=dict(color='#2a3a4a')),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#3a4a5a', size=11)),
    margin=dict(l=0, r=0, t=48, b=0),
    hovermode='x unified',
    hoverlabel=dict(bgcolor='#0c1018', font=dict(color='#d4c5a9', family='DM Mono')),
)

if st.session_state.get('analyzed') and st.session_state.get('tickers'):
    for ticker in st.session_state['tickers']:
        with st.spinner(f"Analyzing {ticker}..."):
            articles = fetch_articles(ticker)
            for article in articles:
                article_id = insert_article(
                    article['ticker'], article['title'], article['description'],
                    article['published_at'], article['source'], article['url']
                )
                if article_id:
                    sentiment_result = analysis_sentiment(article['description'] or article['title'])
                    insert_sentiment(article_id, sentiment_result['label'], sentiment_result['score'])

        data = get_articles_by_ticker(ticker)
        if data:
            df = pd.DataFrame(data, columns=['id', 'title', 'published_at', 'label', 'score'])
            df['date'] = pd.to_datetime(df['published_at']).dt.date
            daily_sentiment = df.groupby('date')['score'].mean().reset_index()
            stock_data = get_stocks_data(ticker, df['published_at'].min()[:10])
            corr = calculate_correlation(daily_sentiment, stock_data)

            st.markdown(f'<div class="ticker-header">{ticker}</div>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1: metric_card("Total Articles", len(df))
            with col2: metric_card("Dominant Sentiment", df['label'].mode()[0].upper())
            with col3: metric_card("Latest Close", f"${stock_data['Close'].iloc[-1]:.2f}")
            with col4: metric_card("Sentiment Correlation", corr if corr is not None else "—")

            avg_score = daily_sentiment['score'].mean()
            if df['label'].mode()[0] == 'negative' and avg_score < 0.5:
                st.markdown(f'<div class="alert-negative">Negative Sentiment Detected &nbsp;·&nbsp; {ticker} &nbsp;·&nbsp; Confidence {avg_score:.2f}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Price vs Sentiment</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=stock_data['Date'], y=stock_data['Close'],
                mode='lines', name='Stock Price',
                line=dict(color='#c8a96e', width=1.5)
            ))
            fig.add_trace(go.Scatter(
                x=daily_sentiment['date'], y=daily_sentiment['score'],
                mode='lines+markers', name='Avg Sentiment',
                line=dict(color='#3a5a7a', width=1.5),
                marker=dict(size=4, color='#3a5a7a'),
                yaxis='y2'
            ))
            fig.update_layout(
                **CHART_LAYOUT,
                title=dict(text=f"{ticker}", font=dict(size=12, color='#2a3a4a', family='DM Mono')),
                yaxis2=dict(
                    overlaying='y', side='right',
                    title=dict(text='Sentiment', font=dict(color='#2a3a4a', size=10)),
                    range=[0, 1], gridcolor='#0f141a', zeroline=False,
                    tickfont=dict(color='#2a3a4a')
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-label">Articles</div>', unsafe_allow_html=True)
            st.dataframe(
                df[['title', 'published_at', 'label', 'score']].style.map(color_sentiment, subset=['label']),
                use_container_width=True, hide_index=True
            )

            st.markdown('<div class="section-label">Word Cloud</div>', unsafe_allow_html=True)
            render_wordcloud(df)

            st.markdown('<div class="section-label">Sentiment Distribution</div>', unsafe_allow_html=True)
            sentiment_counts = df['label'].value_counts().reset_index()
            sentiment_counts.columns = ['label', 'count']
            fig_donut = go.Figure(go.Pie(
                labels=sentiment_counts['label'].str.capitalize(),
                values=sentiment_counts['count'],
                hole=0.65,
                marker=dict(colors=['#4a7c59', '#8b1a1a', '#3a4a5a']),
                textfont=dict(family='DM Mono, monospace', color='#2a3a4a'),
                hovertemplate='%{label}: %{value} articles<extra></extra>'
            ))
            fig_donut.update_layout(
                paper_bgcolor='#080c10',
                plot_bgcolor='#080c10',
                font=dict(family='DM Mono, monospace', color='#2a3a4a', size=11),
                showlegend=True,
                margin=dict(l=0, r=0, t=0, b=0),
                height=300,
                hoverlabel=dict(bgcolor='#0c1018', font=dict(color='#d4c5a9', family='DM Mono')),
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            st.markdown('<div class="section-label">Drill Down</div>', unsafe_allow_html=True)
            selected_date = st.selectbox("", options=sorted(df['date'].unique()), key=f"selectbox_{ticker}")
            st.dataframe(
                df[df['date'] == selected_date][['title', 'published_at', 'label', 'score']].style.map(color_sentiment, subset=['label']),
                use_container_width=True, hide_index=True
            )

            st.markdown('<div class="section-label">Backtest — Sentiment Strategy vs Buy & Hold</div>', unsafe_allow_html=True)
            bt = run_backtest(daily_sentiment, stock_data)
            if bt is not None:
                fig_bt = go.Figure()
                fig_bt.add_trace(go.Scatter(
                    x=bt['Date'], y=bt['cumulative_market'],
                    mode='lines', name='Buy & Hold',
                    line=dict(color='#3a5a7a', width=1.5)
                ))
                fig_bt.add_trace(go.Scatter(
                    x=bt['Date'], y=bt['cumulative_strategy'],
                    mode='lines', name='Sentiment Strategy',
                    line=dict(color='#c8a96e', width=1.5)
                ))
                fig_bt.update_layout(
                    **CHART_LAYOUT,
                    title=dict(text=f"{ticker} — Strategy Returns", font=dict(size=12, color='#2a3a4a', family='DM Mono')),
                    yaxis_tickformat='.2%'
                )
                st.plotly_chart(fig_bt, use_container_width=True)

                final_market = bt['cumulative_market'].iloc[-1] - 1
                final_strategy = bt['cumulative_strategy'].iloc[-1] - 1
                col1, col2 = st.columns(2)
                with col1: metric_card("Buy & Hold Return", f"{final_market:.2%}")
                with col2: metric_card("Sentiment Strategy Return", f"{final_strategy:.2%}")
            else:
                st.markdown('<p style="color:#2a3a4a;font-size:12px;">Insufficient data for backtest.</p>', unsafe_allow_html=True)

        else:
            st.warning(f"No data for {ticker}.")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)