import unittest
import os
import tempfile
import spacy
from src.data.feature_engineering import TheoremFeatureExtractor

class TestTheoremFeatureExtractor(unittest.TestCase):
    """Test cases for TheoremFeatureExtractor"""
    
    def setUp(self):
        """Set up test environment"""
        # Create test configuration
        self.config = {
            'features': {
                'text': {
                    'use_spacy': True,
                    'spacy_model': 'en_core_web_sm',
                    'max_tokens': 512,
                    'min_token_freq': 2
                },
                'structural': {
                    'count_symbols': True,
                    'count_steps': True,
                    'analyze_complexity': True
                },
                'domain_specific': {
                    'use_keywords': True,
                    'keyword_weight': 1.5,
                    'context_window': 5
                }
            }
        }
        
        # Create test theorem
        self.test_theorem = {
            'id': 'test_1',
            'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
            'domain': 'algebra',
            'difficulty': 'easy',
            'prerequisites': ['Properties of real numbers'],
            'proof': 'Let x and y be positive real numbers. Since x > 0, y > 0, their product xy > 0. [QED]'
        }
        
        # Initialize feature extractor
        self.feature_extractor = TheoremFeatureExtractor(self.config)
        
    def test_extract_text_features(self):
        """Test text feature extraction"""
        features = self.feature_extractor.extract_text_features(self.test_theorem)
        
        # Check feature presence
        self.assertIn('token_count', features)
        self.assertIn('sentence_count', features)
        self.assertIn('avg_word_length', features)
        self.assertIn('unique_tokens', features)
        
        # Check feature types
        self.assertIsInstance(features['token_count'], int)
        self.assertIsInstance(features['sentence_count'], int)
        self.assertIsInstance(features['avg_word_length'], float)
        self.assertIsInstance(features['unique_tokens'], int)
        
        # Check feature values
        self.assertGreater(features['token_count'], 0)
        self.assertGreater(features['sentence_count'], 0)
        self.assertGreater(features['avg_word_length'], 0)
        
    def test_extract_structural_features(self):
        """Test structural feature extraction"""
        features = self.feature_extractor.extract_structural_features(self.test_theorem)
        
        # Check feature presence
        self.assertIn('symbol_count', features)
        self.assertIn('step_count', features)
        self.assertIn('complexity_score', features)
        
        # Check feature types
        self.assertIsInstance(features['symbol_count'], int)
        self.assertIsInstance(features['step_count'], int)
        self.assertIsInstance(features['complexity_score'], float)
        
        # Check feature values
        self.assertGreaterEqual(features['symbol_count'], 0)
        self.assertGreaterEqual(features['step_count'], 0)
        self.assertGreaterEqual(features['complexity_score'], 0)
        
    def test_extract_domain_features(self):
        """Test domain-specific feature extraction"""
        features = self.feature_extractor.extract_domain_features(self.test_theorem)
        
        # Check feature presence
        self.assertIn('domain_keywords', features)
        self.assertIn('keyword_density', features)
        self.assertIn('domain_complexity', features)
        
        # Check feature types
        self.assertIsInstance(features['domain_keywords'], list)
        self.assertIsInstance(features['keyword_density'], float)
        self.assertIsInstance(features['domain_complexity'], float)
        
        # Check feature values
        self.assertGreaterEqual(features['keyword_density'], 0)
        self.assertGreaterEqual(features['domain_complexity'], 0)
        
    def test_extract_all_features(self):
        """Test complete feature extraction"""
        features = self.feature_extractor.extract_features(self.test_theorem)
        
        # Check all feature categories
        self.assertIn('text_features', features)
        self.assertIn('structural_features', features)
        self.assertIn('domain_features', features)
        
        # Check feature dictionaries
        self.assertIsInstance(features['text_features'], dict)
        self.assertIsInstance(features['structural_features'], dict)
        self.assertIsInstance(features['domain_features'], dict)
        
    def test_invalid_theorem(self):
        """Test feature extraction with invalid theorem"""
        invalid_theorem = {
            'id': 'invalid_1',
            'domain': 'algebra'
            # Missing required fields
        }
        
        with self.assertRaises(ValueError):
            self.feature_extractor.extract_features(invalid_theorem)
            
    def test_clean_text(self):
        """Test text cleaning function"""
        test_text = "  x^2 + y^2 = z^2  "
        cleaned_text = self.feature_extractor._clean_text(test_text)
        
        # Check cleaned text
        self.assertEqual(cleaned_text, "x^2 + y^2 = z^2")
        
    def test_calculate_complexity(self):
        """Test complexity calculation"""
        test_text = "Let x be a real number. If x > 0, then x^2 > 0."
        complexity = self.feature_extractor._calculate_complexity(test_text)
        
        # Check complexity score
        self.assertIsInstance(complexity, float)
        self.assertGreaterEqual(complexity, 0)
        
if __name__ == '__main__':
    unittest.main() 