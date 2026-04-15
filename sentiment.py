from transformers import pipeline

pipe = pipeline("text-classification", model = "ProsusAI/finbert")

def analysis_sentiment(text):
    text = text[:512]
    result = pipe(text)[0]
    return {'label': result['label'], 'score': round(result['score'] ,4)}