import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import yfinance as yf
import pandas as pd

class SentimentAnalyzer:
    def __init__(self):
        nltk.download('vader_lexicon', quiet=True)
        self.sia = SentimentIntensityAnalyzer()

    def analyze_news(self, symbol: str) -> dict:
        try:
            stock = yf.Ticker(symbol)
            news = stock.news[:5]
            
            sentiments = []
            for article in news:
                sentiment = self.sia.polarity_scores(article['title'])
                sentiments.append(sentiment['compound'])
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            return {
                'sentiment_score': avg_sentiment,
                'sentiment_label': self._get_sentiment_label(avg_sentiment),
                'news_count': len(news)
            }
        except:
            return {'sentiment_score': 0, 'sentiment_label': 'Neutral', 'news_count': 0}

    def _get_sentiment_label(self, score: float) -> str:
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
