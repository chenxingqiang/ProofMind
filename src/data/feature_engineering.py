"""
Feature engineering module for theorem data.
"""

import logging
import re
from typing import Dict, Any

import numpy as np
import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

class TheoremFeatureExtractor:
    """Feature extractor for theorem data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the feature extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            logger.warning("Downloading spaCy model 'en_core_web_sm'...")
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
        
        # Compile regex patterns
        self.math_symbol_pattern = re.compile(r'[∈∀∃→≥≤≠∧∨=\+\-\*\/\(\)\[\]\{\}]')
        self.number_pattern = re.compile(r'\d+')
    
    def extract_features(self, theorem: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from a theorem.
        
        Args:
            theorem: Theorem dictionary
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # Process text with spaCy
            statement_doc = self.nlp(theorem['statement'])
            proof_doc = self.nlp(theorem['proof'])
            
            # Extract basic features
            features.update(self._extract_length_features(theorem))
            features.update(self._extract_complexity_features(theorem))
            features.update(self._extract_linguistic_features(statement_doc, proof_doc))
            features.update(self._extract_mathematical_features(theorem))
            
        except Exception as e:
            logger.error(f"Error extracting features for theorem {theorem.get('id', 'unknown')}: {str(e)}")
            # Return default features
            features = self._get_default_features()
        
        return features
    
    def _get_default_features(self) -> Dict[str, float]:
        """Get default feature values when extraction fails."""
        return {
            'statement_length': 0.0,
            'proof_length': 0.0,
            'num_prerequisites': 0.0,
            'normalized_statement_length': 0.0,
            'normalized_proof_length': 0.0,
            'difficulty_score': 0.5,
            'prerequisite_complexity': 0.0,
            'num_math_symbols': 0.0,
            'num_numbers': 0.0,
            'linguistic_complexity': 0.0
        }
    
    def _extract_length_features(self, theorem: Dict[str, Any]) -> Dict[str, float]:
        """Extract length-based features.
        
        Args:
            theorem: Theorem dictionary
            
        Returns:
            Dictionary of length features
        """
        features = {
            'statement_length': len(theorem['statement'].split()),
            'proof_length': len(theorem['proof'].split()),
            'num_prerequisites': len(theorem.get('prerequisites', [])),
        }
        
        # Normalize lengths
        max_statement_length = self.config.get('features', {}).get('max_statement_length', 1000)
        max_proof_length = self.config.get('features', {}).get('max_proof_length', 2000)
        
        features['normalized_statement_length'] = features['statement_length'] / max_statement_length
        features['normalized_proof_length'] = features['proof_length'] / max_proof_length
        
        return features
    
    def _extract_complexity_features(self, theorem: Dict[str, Any]) -> Dict[str, float]:
        """Extract complexity-based features.
        
        Args:
            theorem: Theorem dictionary
            
        Returns:
            Dictionary of complexity features
        """
        features = {}
        
        # Difficulty score (convert categorical to numeric)
        difficulty_map = {
            'easy': 0.0,
            'medium': 0.5,
            'hard': 1.0
        }
        features['difficulty_score'] = difficulty_map.get(theorem.get('difficulty', 'medium'), 0.5)
        
        # Prerequisite complexity
        prerequisites = theorem.get('prerequisites', [])
        features['prerequisite_complexity'] = len(prerequisites) / 10.0  # Normalize by assuming max 10 prerequisites
        
        return features
    
    def _extract_linguistic_features(self, statement_doc: Language, proof_doc: Language) -> Dict[str, float]:
        """Extract linguistic features using spaCy.
        
        Args:
            statement_doc: Processed statement document
            proof_doc: Processed proof document
            
        Returns:
            Dictionary of linguistic features
        """
        features = {}
        
        # Count mathematical symbols
        statement_symbols = len(self.math_symbol_pattern.findall(statement_doc.text))
        proof_symbols = len(self.math_symbol_pattern.findall(proof_doc.text))
        features['num_math_symbols'] = statement_symbols + proof_symbols
        
        # Count numbers
        statement_numbers = len(self.number_pattern.findall(statement_doc.text))
        proof_numbers = len(self.number_pattern.findall(proof_doc.text))
        features['num_numbers'] = statement_numbers + proof_numbers
        
        # Linguistic complexity (based on sentence length and depth)
        avg_sent_length = np.mean([len(sent) for sent in statement_doc.sents] + [len(sent) for sent in proof_doc.sents])
        features['linguistic_complexity'] = avg_sent_length / 50.0  # Normalize by assuming max length of 50
        
        return features
    
    def _extract_mathematical_features(self, theorem: Dict[str, Any]) -> Dict[str, float]:
        """Extract mathematics-specific features.
        
        Args:
            theorem: Theorem dictionary
            
        Returns:
            Dictionary of mathematical features
        """
        features = {}
        
        # Count mathematical symbols in statement and proof
        statement_symbols = len(self.math_symbol_pattern.findall(theorem['statement']))
        proof_symbols = len(self.math_symbol_pattern.findall(theorem['proof']))
        features['math_symbol_density'] = (statement_symbols + proof_symbols) / (len(theorem['statement']) + len(theorem['proof']))
        
        return features
