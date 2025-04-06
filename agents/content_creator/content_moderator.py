"""
Content Moderator - Module for checking content appropriateness before publishing.

Uses OpenAI's Moderation API and custom filtering to ensure content
meets platform guidelines and brand standards.
"""

import logging
import re
import os
import openai
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ContentModerator")

class ContentModerator:
    """
    Checks content for appropriateness before publishing.
    Uses OpenAI's Moderation API and custom filtering rules.
    """
    
    def __init__(self, custom_filter_words: Optional[List[str]] = None):
        """
        Initialize the ContentModerator.
        
        Args:
            custom_filter_words: Optional list of additional words to filter
        """
        # Default list of potentially problematic terms for educational/science content
        self.filter_words = custom_filter_words or [
            # Political terms
            "liberal", "conservative", "republican", "democrat", "leftist", "rightist",
            # Religious terms
            "god", "allah", "jesus", "buddha", "hindu", "christian", "muslim", "jewish",
            # Potentially problematic product terms
            "better than competitors", "best in the world", "guaranteed results",
            # Extreme claims
            "proven", "revolutionary", "groundbreaking", "never before seen",
            # Inappropriate language markers
            "wtf", "damn", "hell", "crap",
        ]
        
        # Load OpenAI API key for moderation
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            logger.warning("OpenAI API key not found. Using only basic content moderation.")
        
        logger.info("ContentModerator initialized with %d filter words", len(self.filter_words))
    
    def check_content(self, content: str) -> bool:
        """
        Check if content is appropriate for publishing.
        
        Args:
            content: Text content to check
            
        Returns:
            True if content is appropriate, False otherwise
        """
        # First run custom filter check
        custom_filter_result = self._custom_filter_check(content)
        if not custom_filter_result["appropriate"]:
            logger.warning("Content failed custom filter check: %s", 
                          ", ".join(custom_filter_result["matched_terms"]))
            return False
        
        # Then run OpenAI Moderation API check if key is available
        if openai.api_key:
            try:
                moderation_result = self._openai_moderation_check(content)
                if not moderation_result["appropriate"]:
                    logger.warning("Content failed OpenAI moderation check: %s",
                                  ", ".join(moderation_result["flagged_categories"]))
                    return False
            except Exception as e:
                logger.error("Error in OpenAI moderation check: %s", str(e))
                # If OpenAI check fails, rely only on custom filter
                return custom_filter_result["appropriate"]
        
        return True
    
    def _custom_filter_check(self, content: str) -> Dict[str, Any]:
        """
        Perform custom word and phrase filtering.
        
        Args:
            content: Text content to check
            
        Returns:
            Dictionary with check results
        """
        content_lower = content.lower()
        matched_terms = []
        
        # Check for each filter word
        for word in self.filter_words:
            # Use word boundary to match whole words only
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            if re.search(pattern, content_lower):
                matched_terms.append(word)
        
        # Check for inappropriate patterns
        patterns = {
            "excessive_caps": r'([A-Z]{4,})',  # 4+ capital letters in a row
            "excessive_exclamation": r'(!{3,})',  # 3+ exclamation marks
            "clickbait": r'\b(you won\'t believe|mind blown|shocking|amazing)\b',
            "unprofessional": r'\b(lol|omg|wtf|lmao|rofl)\b'
        }
        
        for name, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                matched_terms.append(f"pattern:{name}")
        
        return {
            "appropriate": len(matched_terms) == 0,
            "matched_terms": matched_terms
        }
    
    def _openai_moderation_check(self, content: str) -> Dict[str, Any]:
        """
        Check content using OpenAI's Moderation API.
        
        Args:
            content: Text content to check
            
        Returns:
            Dictionary with check results
        """
        try:
            response = openai.Moderation.create(input=content)
            result = response.results[0]
            
            # Check if content is flagged
            is_appropriate = not result.flagged
            
            # Extract flagged categories if any
            flagged_categories = []
            if result.flagged:
                for category, flagged in result.categories.items():
                    if flagged:
                        flagged_categories.append(category)
            
            return {
                "appropriate": is_appropriate,
                "flagged_categories": flagged_categories,
                "scores": result.category_scores
            }
            
        except Exception as e:
            logger.error("Error in OpenAI moderation API call: %s", str(e))
            raise 