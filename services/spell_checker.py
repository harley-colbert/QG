# File Hierarchy: services/spell_checker.py
# This module provides spell-checking functionality using the pyspellchecker package.
# It offers methods for tokenizing text, checking spelling, and retrieving suggestions.
# The implementation adheres to MVVM principles, uses Python 3.12.9 with full type annotations,
# and includes production-ready logging and error handling.

from __future__ import annotations
import re
import logging
import os
import sys
from typing import List, Tuple, Dict, Any
from spellchecker import SpellChecker

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SpellCheckerService:
    """
    Provides spell-checking functionality using the pyspellchecker package.
    
    Methods:
        tokenize(text: str) -> List[Tuple[str, int, int]]:
            Tokenizes the input text into words with their positions.
        check_text(text: str) -> Dict[str, Dict[str, Any]]:
            Checks the spelling of the provided text and returns details on misspelled words.
        check_word(word: str) -> Tuple[bool, List[str]]:
            Checks if a single word is spelled correctly and provides suggestions if not.
    """
    def __init__(self, language: str = "en") -> None:
        """
        Initialize the SpellCheckerService with the specified language.
        
        Args:
            language (str): Language code for spell-checking, default is "en".
        """
        try:
            if getattr(sys, "frozen", False):
                base_path = sys._MEIPASS  # type: ignore
            else:
                base_path = os.path.dirname(__file__)
            local_dict_path = os.path.join(base_path, "en.json.gz")
            if os.path.exists(local_dict_path):
                logger.info(f"Dictionary file found at: {local_dict_path}")
                self.spell = SpellChecker(language=language, local_dictionary=local_dict_path)
                logger.info(f"SpellChecker initialized with local dictionary '{local_dict_path}'")
            else:
                logger.warning(f"Dictionary file not found at: {local_dict_path}")
                self.spell = SpellChecker(language=language)
        except Exception as e:
            logger.error(f"Error initializing SpellCheckerService: {e}", exc_info=True)
            self.spell = SpellChecker(language=language)

    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Tokenizes the input text into words and returns a list of tuples:
        (word, start_index, end_index).
        
        Args:
            text (str): The text to tokenize.
        
        Returns:
            List[Tuple[str, int, int]]: List of tokens with their positions.
        """
        tokens: List[Tuple[str, int, int]] = []
        try:
            for match in re.finditer(r'\b\w+\b', text):
                tokens.append((match.group(), match.start(), match.end()))
            logger.debug(f"Tokenized text into {len(tokens)} tokens.")
            return tokens
        except Exception as e:
            logger.error(f"Error tokenizing text: {e}", exc_info=True)
            return []

    def _get_context(self, text: str, start: int, end: int, context_size: int = 40) -> str:
        """
        Retrieves a snippet of text around the given indices.
        
        Args:
            text (str): The full text.
            start (int): Start index of the word.
            end (int): End index of the word.
            context_size (int): Number of characters to include before and after the word.
        
        Returns:
            str: Context snippet.
        """
        try:
            ctx_start = max(0, start - context_size)
            ctx_end = min(len(text), end + context_size)
            context = text[ctx_start:ctx_end]
            if ctx_start > 0:
                context = "..." + context
            if ctx_end < len(text):
                context = context + "..."
            return context
        except Exception as e:
            logger.error(f"Error getting context: {e}", exc_info=True)
            return ""

    def check_text(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Checks the spelling of the given text.
        Returns a dictionary mapping each misspelled word to its details including position,
        suggestions, and context.
        
        Args:
            text (str): The text to check.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of misspelled words and details.
        """
        if not text:
            logger.debug("No text provided to check_text.")
            return {}
        try:
            tokens = self.tokenize(text)
            issues: Dict[str, Dict[str, Any]] = {}
            for word, start, end in tokens:
                if word.lower() not in self.spell:
                    suggestions = list(self.spell.candidates(word))
                    context = self._get_context(text, start, end)
                    issues[word] = {
                        "position": (start, end),
                        "suggestions": suggestions,
                        "context": context
                    }
            logger.debug(f"check_text found {len(issues)} issues.")
            return issues
        except Exception as e:
            logger.error(f"Error in check_text: {e}", exc_info=True)
            return {}

    def check_word(self, word: str) -> Tuple[bool, List[str]]:
        """
        Checks a single word for correctness.
        
        Args:
            word (str): The word to check.
        
        Returns:
            Tuple[bool, List[str]]: A tuple containing a boolean indicating if the word is correct
                                    and a list of suggestions if it is not.
        """
        if not word:
            return True, []
        try:
            if word.lower() in self.spell:
                return True, []
            else:
                suggestions = list(self.spell.candidates(word))
                return False, suggestions
        except Exception as e:
            logger.error(f"Error checking word '{word}': {e}", exc_info=True)
            return True, []
