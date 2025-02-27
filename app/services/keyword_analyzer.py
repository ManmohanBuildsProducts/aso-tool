import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from typing import List, Dict, Any
import re
from .app_scraper import AppScraper
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class KeywordAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.app_scraper = AppScraper()

    async def analyze_app_keywords(self, app_id: str) -> Dict[str, Any]:
        """
        Analyze keywords from an app's title and description
        """
        try:
            app_details = await self.app_scraper.get_app_details(app_id)
            
            # Extract text from app details
            title = app_details.get('title', '')
            description = app_details.get('description', '')
            
            # Combine title and description for analysis
            full_text = f"{title} {description}"
            
            # Extract keywords
            keywords = self._extract_keywords(full_text)
            
            # Get keyword density
            keyword_density = self._calculate_keyword_density(keywords)
            
            # Get title specific keywords
            title_keywords = self._extract_keywords(title)
            
            return {
                "app_id": app_id,
                "title_keywords": list(title_keywords),
                "top_keywords": dict(keyword_density.most_common(20)),
                "keyword_count": len(keywords),
                "title_length": len(title),
                "description_length": len(description)
            }
        except Exception as e:
            logger.error(f"Error analyzing keywords for {app_id}: {str(e)}")
            raise

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = self.tokenizer.tokenize(text)
        
        # Remove stop words and short words
        keywords = [word for word in tokens 
                   if word not in self.stop_words 
                   and len(word) > 2
                   and not word.isnumeric()]
        
        return keywords

    def _calculate_keyword_density(self, keywords: List[str]) -> Counter:
        """
        Calculate keyword density from a list of keywords
        """
        return Counter(keywords)

    async def compare_keywords(self, app_id: str, competitor_ids: List[str]) -> Dict[str, Any]:
        """
        Compare keywords between an app and its competitors
        """
        try:
            # Analyze main app
            main_app_analysis = await self.analyze_app_keywords(app_id)
            
            # Analyze competitors
            competitor_analyses = []
            for comp_id in competitor_ids:
                try:
                    comp_analysis = await self.analyze_app_keywords(comp_id)
                    competitor_analyses.append(comp_analysis)
                except Exception as e:
                    logger.warning(f"Error analyzing competitor {comp_id}: {str(e)}")
                    continue
            
            # Find common and unique keywords
            main_keywords = set(main_app_analysis["top_keywords"].keys())
            competitor_keywords = set()
            for comp in competitor_analyses:
                competitor_keywords.update(comp["top_keywords"].keys())
            
            common_keywords = main_keywords.intersection(competitor_keywords)
            unique_keywords = main_keywords - competitor_keywords
            
            return {
                "main_app": {
                    "app_id": app_id,
                    "analysis": main_app_analysis
                },
                "competitors": [
                    {"app_id": comp["app_id"], "analysis": comp}
                    for comp in competitor_analyses
                ],
                "keyword_comparison": {
                    "common_keywords": list(common_keywords),
                    "unique_keywords": list(unique_keywords),
                    "competitor_keywords": list(competitor_keywords - main_keywords)
                }
            }
        except Exception as e:
            logger.error(f"Error comparing keywords: {str(e)}")
            raise