import unittest
import os
import json
import tempfile
from src.data.data_loader import TheoremDataLoader

class TestTheoremDataLoader(unittest.TestCase):
    """Test cases for TheoremDataLoader"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config = {
            'data': {
                'base_path': self.test_dir,
                'train_path': 'train',
                'val_path': 'val',
                'test_path': 'test',
                'domains': ['algebra', 'analysis']
            }
        }
        
        # Create test data
        self.test_theorems = {
            'algebra': [
                {
                    'id': 'algebra_1',
                    'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
                    'domain': 'algebra',
                    'difficulty': 'easy',
                    'prerequisites': ['Properties of real numbers'],
                    'proof': 'Let x and y be positive real numbers...'
                }
            ],
            'analysis': [
                {
                    'id': 'analysis_1',
                    'statement': 'The limit of 1/n as n approaches infinity is 0',
                    'domain': 'analysis',
                    'difficulty': 'medium',
                    'prerequisites': ['Definition of limit'],
                    'proof': 'Given ε > 0, choose N...'
                }
            ]
        }
        
        # Save test data
        for domain in self.test_theorems:
            for split in ['train', 'val', 'test']:
                path = os.path.join(self.test_dir, split, f"{domain}_theorems.json")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    json.dump(self.test_theorems[domain], f)
                    
        # Initialize data loader
        self.data_loader = TheoremDataLoader(self.config)
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.test_dir)
        
    def test_load_theorems_all_domains(self):
        """Test loading theorems from all domains"""
        theorems = self.data_loader.load_theorems(split='train')
        
        # Check number of theorems
        self.assertEqual(len(theorems), 2)
        
        # Check theorem content
        domains = set(theorem['domain'] for theorem in theorems)
        self.assertEqual(domains, {'algebra', 'analysis'})
        
    def test_load_theorems_single_domain(self):
        """Test loading theorems from a single domain"""
        theorems = self.data_loader.load_theorems(domains=['algebra'], split='train')
        
        # Check number of theorems
        self.assertEqual(len(theorems), 1)
        
        # Check theorem content
        self.assertEqual(theorems[0]['domain'], 'algebra')
        
    def test_load_theorems_invalid_domain(self):
        """Test loading theorems with invalid domain"""
        with self.assertRaises(ValueError):
            self.data_loader.load_theorems(domains=['invalid_domain'], split='train')
            
    def test_load_theorems_invalid_split(self):
        """Test loading theorems with invalid split"""
        with self.assertRaises(ValueError):
            self.data_loader.load_theorems(split='invalid_split')
            
    def test_theorem_preprocessing(self):
        """Test theorem preprocessing"""
        theorems = self.data_loader.load_theorems(split='train')
        
        for theorem in theorems:
            # Check required fields
            self.assertIn('id', theorem)
            self.assertIn('statement', theorem)
            self.assertIn('domain', theorem)
            self.assertIn('proof', theorem)
            
            # Check field types
            self.assertIsInstance(theorem['id'], str)
            self.assertIsInstance(theorem['statement'], str)
            self.assertIsInstance(theorem['domain'], str)
            self.assertIsInstance(theorem['prerequisites'], list)
            
    def test_clean_text(self):
        """Test text cleaning function"""
        test_text = "  This is a  test   text  with extra  spaces  "
        cleaned_text = self.data_loader._clean_text(test_text)
        
        # Check cleaned text
        self.assertEqual(cleaned_text, "This is a test text with extra spaces")
        
if __name__ == '__main__':
    unittest.main() 