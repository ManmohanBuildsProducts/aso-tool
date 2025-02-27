import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

def test_nltk():
    # Test tokenization
    text = "Hello, this is a test sentence!"
    tokens = word_tokenize(text)
    print("Tokenization test:", tokens)

    # Test stopwords
    stop_words = set(stopwords.words('english'))
    print("Stopwords test:", list(stop_words)[:5])

    # Test sentiment analysis
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    print("Sentiment test:", sentiment)

if __name__ == "__main__":
    test_nltk()