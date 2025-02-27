from typing import Dict, Any, List
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
from app.services.app_scraper import AppScraper

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class MetadataAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.app_scraper = AppScraper()
        
        # Ideal metadata characteristics
        self.IDEAL_TITLE_LENGTH = 50  # characters
        self.IDEAL_DESC_LENGTH = 4000  # characters
        self.IDEAL_KEYWORD_DENSITY = 0.02  # 2%
        self.MIN_KEYWORDS = 5
        self.MAX_KEYWORDS = 10

    async def analyze_metadata(self, app_id: str) -> Dict[str, Any]:
        """
        Analyze app metadata including title and description
        """
        try:
            app_details = await self.app_scraper.get_app_details(app_id)
            
            title = app_details.get('title', '')
            description = app_details.get('description', '')
            
            # Analyze different components
            title_analysis = self._analyze_title(title)
            desc_analysis = self._analyze_description(description)
            keyword_analysis = self._analyze_keywords(title, description)
            
            return {
                "app_id": app_id,
                "title_analysis": title_analysis,
                "description_analysis": desc_analysis,
                "keyword_analysis": keyword_analysis,
                "overall_score": self._calculate_overall_score(
                    title_analysis,
                    desc_analysis,
                    keyword_analysis
                ),
                "recommendations": self._generate_recommendations(
                    title_analysis,
                    desc_analysis,
                    keyword_analysis
                )
            }
        except Exception as e:
            logger.error(f"Error analyzing metadata for {app_id}: {str(e)}")
            raise

    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """
        Analyze app title for optimization
        """
        length = len(title)
        words = len(title.split())
        
        # Calculate length score
        length_score = max(0, 1 - abs(length - self.IDEAL_TITLE_LENGTH) / self.IDEAL_TITLE_LENGTH)
        
        # Check for special characters
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', title))
        
        # Calculate keyword density
        keywords = self._extract_keywords(title)
        keyword_density = len(keywords) / words if words > 0 else 0
        
        return {
            "length": length,
            "word_count": words,
            "special_characters": special_chars,
            "keywords": keywords,
            "keyword_density": keyword_density,
            "length_score": length_score,
            "overall_score": self._calculate_title_score(
                length_score,
                keyword_density,
                special_chars
            )
        }

    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze app description for optimization
        """
        length = len(description)
        paragraphs = len(description.split('\n\n'))
        sentences = len(nltk.sent_tokenize(description))
        
        # Calculate readability metrics
        words = description.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Calculate keyword density
        keywords = self._extract_keywords(description)
        keyword_density = len(keywords) / len(words) if words else 0
        
        # Analyze structure
        has_features = bool(re.search(r'features|what\'s new|highlights', description.lower()))
        has_calls_to_action = bool(re.search(r'download|install|try|get|now', description.lower()))
        
        return {
            "length": length,
            "paragraph_count": paragraphs,
            "sentence_count": sentences,
            "avg_word_length": avg_word_length,
            "keywords": keywords,
            "keyword_density": keyword_density,
            "has_feature_list": has_features,
            "has_calls_to_action": has_calls_to_action,
            "readability_score": self._calculate_readability_score(
                avg_word_length,
                sentences,
                paragraphs
            ),
            "overall_score": self._calculate_description_score(
                length,
                keyword_density,
                has_features,
                has_calls_to_action
            )
        }

    def _analyze_keywords(self, title: str, description: str) -> Dict[str, Any]:
        """
        Analyze keyword usage and distribution
        """
        title_keywords = self._extract_keywords(title)
        desc_keywords = self._extract_keywords(description)
        
        # Find common and unique keywords
        common_keywords = set(title_keywords) & set(desc_keywords)
        unique_title_keywords = set(title_keywords) - set(desc_keywords)
        
        # Calculate keyword distribution
        all_keywords = title_keywords + desc_keywords
        keyword_freq = Counter(all_keywords)
        
        return {
            "title_keywords": list(title_keywords),
            "description_keywords": list(desc_keywords),
            "common_keywords": list(common_keywords),
            "unique_title_keywords": list(unique_title_keywords),
            "keyword_frequency": dict(keyword_freq),
            "total_unique_keywords": len(set(all_keywords)),
            "keyword_distribution_score": self._calculate_keyword_distribution_score(
                keyword_freq
            )
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text
        """
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        
        # Remove stop words and short words
        keywords = [
            word for word in tokens
            if word not in self.stop_words
            and len(word) > 2
            and word.isalnum()
        ]
        
        return keywords

    def _calculate_title_score(self, length_score: float, keyword_density: float, special_chars: int) -> float:
        """
        Calculate overall title optimization score
        """
        # Penalize for too many special characters
        special_char_penalty = max(0, 1 - (special_chars * 0.1))
        
        # Calculate keyword density score
        keyword_score = max(0, 1 - abs(keyword_density - self.IDEAL_KEYWORD_DENSITY) / self.IDEAL_KEYWORD_DENSITY)
        
        # Weighted average
        return (length_score * 0.4 + keyword_score * 0.4 + special_char_penalty * 0.2)

    def _calculate_description_score(self, length: int, keyword_density: float,
                                   has_features: bool, has_cta: bool) -> float:
        """
        Calculate overall description optimization score
        """
        # Length score
        length_score = max(0, 1 - abs(length - self.IDEAL_DESC_LENGTH) / self.IDEAL_DESC_LENGTH)
        
        # Keyword density score
        keyword_score = max(0, 1 - abs(keyword_density - self.IDEAL_KEYWORD_DENSITY) / self.IDEAL_KEYWORD_DENSITY)
        
        # Structure score
        structure_score = (has_features + has_cta) / 2
        
        # Weighted average
        return (length_score * 0.3 + keyword_score * 0.4 + structure_score * 0.3)

    def _calculate_keyword_distribution_score(self, keyword_freq: Counter) -> float:
        """
        Calculate keyword distribution optimization score
        """
        unique_keywords = len(keyword_freq)
        
        # Check if number of keywords is within ideal range
        keyword_count_score = max(0, 1 - abs(unique_keywords - (self.MIN_KEYWORDS + self.MAX_KEYWORDS)/2) / self.MAX_KEYWORDS)
        
        # Check keyword frequency distribution
        freq_values = list(keyword_freq.values())
        avg_freq = sum(freq_values) / len(freq_values) if freq_values else 0
        freq_score = max(0, 1 - abs(avg_freq - 2) / 2)  # Ideal average frequency is 2
        
        return (keyword_count_score * 0.6 + freq_score * 0.4)

    def _calculate_readability_score(self, avg_word_length: float,
                                   sentence_count: int, paragraph_count: int) -> float:
        """
        Calculate readability score based on text structure
        """
        # Ideal values
        IDEAL_WORD_LENGTH = 5.5
        IDEAL_SENTENCES_PER_PARA = 3
        
        # Calculate component scores
        word_length_score = max(0, 1 - abs(avg_word_length - IDEAL_WORD_LENGTH) / IDEAL_WORD_LENGTH)
        
        sentences_per_para = sentence_count / paragraph_count if paragraph_count > 0 else 0
        structure_score = max(0, 1 - abs(sentences_per_para - IDEAL_SENTENCES_PER_PARA) / IDEAL_SENTENCES_PER_PARA)
        
        return (word_length_score * 0.5 + structure_score * 0.5)

    def _calculate_overall_score(self, title_analysis: Dict[str, Any],
                               desc_analysis: Dict[str, Any],
                               keyword_analysis: Dict[str, Any]) -> float:
        """
        Calculate overall metadata optimization score
        """
        title_score = title_analysis["overall_score"]
        desc_score = desc_analysis["overall_score"]
        keyword_score = keyword_analysis["keyword_distribution_score"]
        
        # Weighted average
        return (title_score * 0.3 + desc_score * 0.4 + keyword_score * 0.3)

    def _generate_recommendations(self, title_analysis: Dict[str, Any],
                                desc_analysis: Dict[str, Any],
                                keyword_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate optimization recommendations based on analysis
        """
        recommendations = []
        
        # Title recommendations
        if title_analysis["length"] > self.IDEAL_TITLE_LENGTH:
            recommendations.append("Consider shortening the title to improve readability")
        if title_analysis["special_characters"] > 2:
            recommendations.append("Reduce special characters in title for better clarity")
        
        # Description recommendations
        if desc_analysis["length"] < self.IDEAL_DESC_LENGTH * 0.8:
            recommendations.append("Add more content to your description for better visibility")
        if not desc_analysis["has_feature_list"]:
            recommendations.append("Include a clear feature list in your description")
        if not desc_analysis["has_calls_to_action"]:
            recommendations.append("Add clear calls-to-action in your description")
        
        # Keyword recommendations
        if keyword_analysis["total_unique_keywords"] < self.MIN_KEYWORDS:
            recommendations.append("Include more relevant keywords in your metadata")
        if len(keyword_analysis["common_keywords"]) < 3:
            recommendations.append("Use more consistent keywords across title and description")
        
        return recommendations