from textblob import TextBlob

def detect_language(text: str) -> str:
    lang_names = {
        'en': 'английский',
        'ru': 'русский',
        'fr': 'французский',
        'de': 'немецкий',
        'es': 'испанский'
    }
    try:
        return lang_names.get(TextBlob(text).detect_language(), "неизвестный")
    except:
        return "неизвестный"

def analyze_sentiment(text: str) -> str:
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0.1: return "positive"
    if sentiment < -0.1: return "negative"
    return "neutral"

def correct_text(text: str) -> str:
    return str(TextBlob(text).correct())