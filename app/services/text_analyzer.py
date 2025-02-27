from typing import Dict, Any, List
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import logging

logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self):
        # ASO-specific limits
        self.LIMITS = {
            'title': {
                'max_chars': 50,
                'max_words': 10,
                'recommended_chars': 30,
                'recommended_words': 5
            },
            'short_description': {
                'max_chars': 80,
                'max_words': 15,
                'recommended_chars': 60,
                'recommended_words': 10
            },
            'full_description': {
                'max_chars': 4000,
                'max_words': 800,
                'recommended_chars': 2000,
                'recommended_words': 400
            }
        }

    def analyze_text(self, text: str, text_type: str = 'full_description') -> Dict[str, Any]:
        """
        Analyze text for character and word counts
        """
        try:
            # Basic counts
            char_count = len(text)
            word_count = len(text.split())
            
            # Detailed analysis
            detailed = self._detailed_analysis(text)
            
            # Get limits for this text type
            limits = self.LIMITS.get(text_type, self.LIMITS['full_description'])
            
            # Calculate scores and recommendations
            optimization = self._calculate_optimization(
                char_count,
                word_count,
                limits
            )
            
            return {
                "basic_metrics": {
                    "character_count": char_count,
                    "word_count": word_count,
                    "sentence_count": detailed["sentence_count"],
                    "paragraph_count": detailed["paragraph_count"]
                },
                "detailed_metrics": {
                    "avg_word_length": detailed["avg_word_length"],
                    "avg_sentence_length": detailed["avg_sentence_length"],
                    "unique_words": detailed["unique_words"],
                    "keyword_density": detailed["keyword_density"]
                },
                "limits": {
                    "max_chars": limits["max_chars"],
                    "max_words": limits["max_words"],
                    "recommended_chars": limits["recommended_chars"],
                    "recommended_words": limits["recommended_words"]
                },
                "optimization": optimization,
                "recommendations": self._generate_recommendations(
                    char_count,
                    word_count,
                    detailed,
                    limits,
                    text_type
                )
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            raise

    def _detailed_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform detailed text analysis
        """
        # Clean text
        text = text.strip()
        
        # Tokenize text
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        
        # Split into paragraphs (handle different line endings)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Calculate averages
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Count unique words
        unique_words = len(set(words))
        
        # Calculate keyword density
        word_freq = Counter(words)
        total_words = len(words)
        keyword_density = {
            word: count/total_words
            for word, count in word_freq.most_common(10)
            if word.isalnum()
        }
        
        return {
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "unique_words": unique_words,
            "keyword_density": keyword_density
        }

    def _calculate_optimization(self, char_count: int, word_count: int,
                              limits: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate optimization scores
        """
        # Character optimization
        char_ratio = char_count / limits["max_chars"]
        char_score = self._calculate_score(
            char_count,
            limits["recommended_chars"],
            limits["max_chars"]
        )
        
        # Word optimization
        word_ratio = word_count / limits["max_words"]
        word_score = self._calculate_score(
            word_count,
            limits["recommended_words"],
            limits["max_words"]
        )
        
        return {
            "character_optimization": {
                "ratio": char_ratio,
                "score": char_score,
                "status": self._get_optimization_status(char_ratio)
            },
            "word_optimization": {
                "ratio": word_ratio,
                "score": word_score,
                "status": self._get_optimization_status(word_ratio)
            },
            "overall_score": (char_score + word_score) / 2
        }

    def _calculate_score(self, current: int, recommended: int, maximum: int) -> float:
        """
        Calculate optimization score based on current value and limits
        """
        if current > maximum:
            return 0.0
        elif current < recommended * 0.5:
            return 0.5 * (current / (recommended * 0.5))
        elif current <= recommended:
            return 0.5 + 0.5 * (current / recommended)
        else:
            return 1.0 - 0.5 * ((current - recommended) / (maximum - recommended))

    def _get_optimization_status(self, ratio: float) -> str:
        """
        Get optimization status based on ratio
        """
        if ratio > 1:
            return "too_long"
        elif ratio > 0.9:
            return "near_limit"
        elif ratio > 0.7:
            return "optimized"
        elif ratio > 0.4:
            return "good"
        else:
            return "too_short"

    def _generate_recommendations(self, char_count: int, word_count: int,
                                detailed: Dict[str, Any], limits: Dict[str, int],
                                text_type: str) -> List[str]:
        """
        Generate recommendations based on analysis
        """
        recommendations = []
        
        # Length recommendations
        if char_count > limits["max_chars"]:
            recommendations.append(f"Reduce text length by {char_count - limits['max_chars']} characters")
        elif char_count < limits["recommended_chars"] * 0.7:
            recommendations.append(f"Add more content (recommended: {limits['recommended_chars']} characters)")
        
        # Word count recommendations
        if word_count > limits["max_words"]:
            recommendations.append(f"Reduce word count by {word_count - limits['max_words']} words")
        elif word_count < limits["recommended_words"] * 0.7:
            recommendations.append(f"Add more words (recommended: {limits['recommended_words']} words)")
        
        # Structure recommendations
        if detailed["avg_sentence_length"] > 20:
            recommendations.append("Consider using shorter sentences for better readability")
        
        if detailed["paragraph_count"] < 3 and text_type == 'full_description':
            recommendations.append("Add more paragraphs to improve readability")
        
        # Keyword recommendations
        if len(detailed["keyword_density"]) < 5:
            recommendations.append("Include more relevant keywords")
        
        max_density = max(detailed["keyword_density"].values())
        if max_density > 0.1:
            recommendations.append("Reduce keyword repetition for better readability")
        
        return recommendations