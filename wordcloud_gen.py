from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st

def render_wordcloud(df):
    text = ' '.join(df['title'].dropna().tolist())
    if not text.strip():
        return
    
    wc = WordCloud(
        width=1200, height=400,
        background_color='#080c10',
        colormap='YlOrBr',
        max_words=50,
        font_path=None,
        collocations=False
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#080c10')
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    plt.close()