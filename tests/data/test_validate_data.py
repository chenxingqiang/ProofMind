import unittest
import json
import os
import tempfile
from src.data.validate_data import TheoremDataValidator

class TestTheoremDataValidator(unittest.TestCase):
    """Test cases for TheoremDataValidator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = TheoremDataValidator()
        
        self.valid_theorem = {
            'id': 'thm1',
            'name': 'Valid Theorem',
            'statement': 'For all x, if x is prime then x is odd or x = 2',
            'domain': 'number_theory',
            'difficulty': 'medium',
            'prerequisites': [],
            'proof_outline': 'Proof by contradiction',
            'metadata': {}
        }
        
        self.invalid_theorem = {
            'id': 'thm2',
            'name': 'Invalid Theorem',
            'statement': 'Some statement',
            'domain': 'invalid_domain',  # Invalid domain
            'difficulty': 'unknown'  # Invalid difficulty
        }
    
    def test_validate_theorem(self):
        """Test validation of a single theorem"""
        # Test valid theorem
        is_valid, error = self.validator.validate_theorem(self.valid_theorem)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Test invalid theorem
        is_valid, error = self.validator.validate_theorem(self.invalid_theorem)
        self.assertFalse(is_valid)
        self.assertIn("domain", error.lower())
    
    def test_validate_dataset(self):
        """Test validation of multiple theorems"""
        dataset = [self.valid_theorem, self.invalid_theorem]
        results = self.validator.validate_dataset(dataset)
        
        self.assertEqual(results['valid_count'], 1)
        self.assertEqual(results['invalid_count'], 1)
        self.assertEqual(len(results['errors']), 1)
    
    def test_check_data_completeness(self):
        """Test data completeness checking"""
        dataset = [self.valid_theorem, self.invalid_theorem]
        metrics = self.validator.check_data_completeness(dataset)
        
        self.assertEqual(metrics['total_theorems'], 2)
        self.assertEqual(metrics['complete_theorems'], 1)
        self.assertIn('domain_distribution', metrics)
        self.assertIn('difficulty_distribution', metrics)
    
    def test_validate_file(self):
        """Test validation of theorem file"""
        # Create temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump([self.valid_theorem], f)
            temp_file = f.name
        
        try:
            # Test valid file
            results = self.validator.validate_file(temp_file)
            self.assertIn('validation', results)
            self.assertIn('completeness', results)
            self.assertEqual(results['validation']['valid_count'], 1)
            
            # Test non-existent file
            results = self.validator.validate_file('nonexistent.json')
            self.assertIn('error', results)
            self.assertIn('not found', results['error'])
            
            # Test invalid JSON file
            with open(temp_file, 'w') as f:
                f.write('invalid json content')
            results = self.validator.validate_file(temp_file)
            self.assertIn('error', results)
            self.assertIn('Invalid JSON', results['error'])
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_required_fields(self):
        """Test validation of required fields"""
        # Test missing required field
        invalid_theorem = self.valid_theorem.copy()
        del invalid_theorem['statement']
        
        is_valid, error = self.validator.validate_theorem(invalid_theorem)
        self.assertFalse(is_valid)
        self.assertIn('statement', error.lower())
    
    def test_field_types(self):
        """Test validation of field types"""
        # Test invalid field type
        invalid_theorem = self.valid_theorem.copy()
        invalid_theorem['prerequisites'] = 'not a list'
        
        is_valid, error = self.validator.validate_theorem(invalid_theorem)
        self.assertFalse(is_valid)
        self.assertIn('prerequisites', error.lower())
    
    def test_enum_values(self):
        """Test validation of enumerated values"""
        # Test invalid difficulty
        invalid_theorem = self.valid_theorem.copy()
        invalid_theorem['difficulty'] = 'impossible'
        
        is_valid, error = self.validator.validate_theorem(invalid_theorem)
        self.assertFalse(is_valid)
        self.assertIn('difficulty', error.lower())
        
        # Test invalid domain
        invalid_theorem = self.valid_theorem.copy()
        invalid_theorem['domain'] = 'invalid_domain'
        
        is_valid, error = self.validator.validate_theorem(invalid_theorem)
        self.assertFalse(is_valid)
        self.assertIn('domain', error.lower())

if __name__ == '__main__':
    unittest.main() 