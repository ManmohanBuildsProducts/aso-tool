from typing import Dict, Any, List
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
from datetime import datetime, timedelta
import re
from textblob import TextBlob

# Download required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon')
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('vader_lexicon')
    nltk.download('punkt')
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class ReviewAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Common feature-related terms
        self.feature_terms = {
            'ui': ['interface', 'ui', 'design', 'layout', 'look'],
            'performance': ['speed', 'fast', 'slow', 'crash', 'bug', 'performance'],
            'usability': ['easy', 'difficult', 'intuitive', 'confusing', 'user-friendly'],
            'reliability': ['stable', 'unstable', 'reliable', 'crash', 'bug'],
            'features': ['feature', 'functionality', 'option', 'capability'],
            'updates': ['update', 'version', 'upgrade', 'latest'],
            'support': ['support', 'help', 'customer service', 'response'],
            'security': ['security', 'privacy', 'safe', 'secure', 'protection']
        }

    async def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze app reviews for sentiment and key insights
        """
        try:
            # Initialize analysis containers
            sentiments = []
            feature_mentions = {category: [] for category in self.feature_terms}
            topics = Counter()
            common_phrases = Counter()
            
            # Time-based containers
            recent_sentiment_trend = []
            sentiment_over_time = {}
            
            # Process each review
            for review in reviews:
                # Extract review data
                text = review.get('text', '')
                score = review.get('score', 0)
                timestamp = review.get('timestamp', '')
                
                if not text:
                    continue
                
                # Analyze sentiment
                sentiment = self._analyze_sentiment(text, score)
                sentiments.append(sentiment)
                
                # Track sentiment over time
                date = self._parse_timestamp(timestamp)
                if date:
                    if date not in sentiment_over_time:
                        sentiment_over_time[date] = []
                    sentiment_over_time[date].append(sentiment['compound'])
                
                # Extract topics and features
                review_topics = self._extract_topics(text)
                topics.update(review_topics)
                
                # Analyze feature mentions
                self._analyze_feature_mentions(text, feature_mentions)
                
                # Extract common phrases
                phrases = self._extract_common_phrases(text)
                common_phrases.update(phrases)
            
            # Calculate overall metrics
            overall_sentiment = self._calculate_overall_sentiment(sentiments)
            sentiment_trends = self._analyze_sentiment_trends(sentiment_over_time)
            key_topics = self._get_key_topics(topics)
            feature_summary = self._summarize_feature_mentions(feature_mentions)
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_trends": sentiment_trends,
                "key_topics": key_topics,
                "feature_analysis": feature_summary,
                "common_phrases": dict(common_phrases.most_common(10)),
                "recommendations": self._generate_recommendations(
                    overall_sentiment,
                    feature_summary,
                    key_topics
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing reviews: {str(e)}")
            raise

    def _analyze_sentiment(self, text: str, score: int) -> Dict[str, float]:
        """
        Analyze sentiment of a single review
        """
        # VADER sentiment analysis
        vader_scores = self.sia.polarity_scores(text)
        
        # TextBlob for additional analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combine with review score
        normalized_score = (score - 3) / 2  # Convert 1-5 scale to -1 to 1
        
        # Weighted combination
        compound = (vader_scores['compound'] * 0.4 + 
                   textblob_polarity * 0.3 +
                   normalized_score * 0.3)
        
        return {
            'pos': vader_scores['pos'],
            'neg': vader_scores['neg'],
            'neu': vader_scores['neu'],
            'compound': compound
        }

    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract main topics from review text
        """
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        
        # Extract bigrams
        bigrams = list(nltk.bigrams(tokens))
        bigram_phrases = [' '.join(bigram) for bigram in bigrams]
        
        # Combine unigrams and bigrams
        all_topics = tokens + bigram_phrases
        
        return all_topics

    def _analyze_feature_mentions(self, text: str, feature_mentions: Dict[str, List[Dict[str, Any]]]):
        """
        Analyze mentions of specific features
        """
        text_lower = text.lower()
        
        for category, terms in self.feature_terms.items():
            for term in terms:
                if term in text_lower:
                    # Get the context around the term
                    context = self._get_context(text_lower, term)
                    
                    # Analyze sentiment for this specific mention
                    sentiment = self.sia.polarity_scores(context)
                    
                    feature_mentions[category].append({
                        'term': term,
                        'context': context,
                        'sentiment': sentiment['compound']
                    })

    def _extract_common_phrases(self, text: str) -> List[str]:
        """
        Extract common meaningful phrases from review
        """
        # Extract 2-3 word phrases
        words = word_tokenize(text.lower())
        bigrams = list(nltk.bigrams(words))
        trigrams = list(nltk.trigrams(words))
        
        # Convert to phrases
        phrases = ([' '.join(bigram) for bigram in bigrams] +
                  [' '.join(trigram) for trigram in trigrams])
        
        # Filter meaningful phrases
        meaningful_phrases = [
            phrase for phrase in phrases
            if not all(word in self.stop_words for word in phrase.split())
        ]
        
        return meaningful_phrases

    def _get_context(self, text: str, term: str, window: int = 5) -> str:
        """
        Get the surrounding context of a term in text
        """
        words = text.split()
        try:
            term_index = words.index(term)
            start = max(0, term_index - window)
            end = min(len(words), term_index + window + 1)
            return ' '.join(words[start:end])
        except ValueError:
            return ''

    def _calculate_overall_sentiment(self, sentiments: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Calculate overall sentiment metrics
        """
        if not sentiments:
            return {
                "compound": 0,
                "positive_ratio": 0,
                "negative_ratio": 0,
                "neutral_ratio": 0
            }
        
        total = len(sentiments)
        compound_avg = sum(s['compound'] for s in sentiments) / total
        
        positive = sum(1 for s in sentiments if s['compound'] > 0.05)
        negative = sum(1 for s in sentiments if s['compound'] < -0.05)
        neutral = total - positive - negative
        
        return {
            "compound": compound_avg,
            "positive_ratio": positive / total,
            "negative_ratio": negative / total,
            "neutral_ratio": neutral / total
        }

    def _analyze_sentiment_trends(self, sentiment_over_time: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Analyze sentiment trends over time
        """
        if not sentiment_over_time:
            return {
                "recent_trend": "neutral",
                "trend_strength": 0,
                "volatility": 0
            }
        
        # Calculate daily averages
        daily_averages = {
            date: sum(sentiments) / len(sentiments)
            for date, sentiments in sentiment_over_time.items()
        }
        
        # Sort by date
        sorted_dates = sorted(daily_averages.keys())
        if len(sorted_dates) < 2:
            return {
                "recent_trend": "neutral",
                "trend_strength": 0,
                "volatility": 0
            }
        
        # Calculate trend
        recent_values = [daily_averages[date] for date in sorted_dates[-7:]]
        trend = sum(recent_values) / len(recent_values)
        
        # Calculate volatility
        volatility = self._calculate_volatility(list(daily_averages.values()))
        
        return {
            "recent_trend": "positive" if trend > 0.05 else "negative" if trend < -0.05 else "neutral",
            "trend_strength": abs(trend),
            "volatility": volatility
        }

    def _calculate_volatility(self, values: List[float]) -> float:
        """
        Calculate volatility of sentiment values
        """
        if len(values) < 2:
            return 0
        
        differences = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
        return sum(differences) / len(differences)

    def _get_key_topics(self, topics: Counter) -> Dict[str, int]:
        """
        Get most significant topics from reviews
        """
        # Filter out common words and short terms
        significant_topics = {
            topic: count for topic, count in topics.items()
            if len(topic) > 3 and topic not in self.stop_words
        }
        
        return dict(Counter(significant_topics).most_common(10))

    def _summarize_feature_mentions(self, feature_mentions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Summarize feature mentions and their sentiments
        """
        summary = {}
        
        for category, mentions in feature_mentions.items():
            if not mentions:
                continue
                
            # Calculate metrics
            total_mentions = len(mentions)
            avg_sentiment = sum(m['sentiment'] for m in mentions) / total_mentions
            
            # Get most common terms
            term_counts = Counter(m['term'] for m in mentions)
            
            summary[category] = {
                "mention_count": total_mentions,
                "average_sentiment": avg_sentiment,
                "common_terms": dict(term_counts.most_common(3)),
                "sentiment_distribution": {
                    "positive": sum(1 for m in mentions if m['sentiment'] > 0.05) / total_mentions,
                    "negative": sum(1 for m in mentions if m['sentiment'] < -0.05) / total_mentions,
                    "neutral": sum(1 for m in mentions if -0.05 <= m['sentiment'] <= 0.05) / total_mentions
                }
            }
        
        return summary

    def _generate_recommendations(self, overall_sentiment: Dict[str, Any],
                                feature_summary: Dict[str, Any],
                                key_topics: Dict[str, int]) -> List[str]:
        """
        Generate recommendations based on analysis
        """
        recommendations = []
        
        # Sentiment-based recommendations
        if overall_sentiment['negative_ratio'] > 0.3:
            recommendations.append("High proportion of negative reviews - address common complaints")
        
        # Feature-based recommendations
        for category, data in feature_summary.items():
            if data['average_sentiment'] < -0.1:
                recommendations.append(f"Improve {category} features - receiving negative feedback")
            elif data['mention_count'] > 10 and data['average_sentiment'] < 0:
                recommendations.append(f"Address user concerns about {category}")
        
        # Topic-based recommendations
        negative_topics = [topic for topic, count in key_topics.items()
                         if count > 5 and self.sia.polarity_scores(topic)['compound'] < -0.1]
        if negative_topics:
            recommendations.append(f"Address frequently mentioned issues: {', '.join(negative_topics)}")
        
        return recommendations

    def _parse_timestamp(self, timestamp: str) -> str:
        """
        Parse timestamp into date string
        """
        try:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = datetime.strptime(timestamp, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return ""