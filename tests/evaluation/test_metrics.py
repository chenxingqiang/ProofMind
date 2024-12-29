import unittest
import numpy as np
from src.evaluate import evaluate_proof_metrics, evaluate_proof_correctness
from src.symbolic.reasoning_engine import SymbolicReasoner

class TestEvaluationMetrics(unittest.TestCase):
    """Test cases for evaluation metrics"""
    
    def setUp(self):
        """Set up test environment"""
        # Create test configuration
        self.config = {
            'model': {
                'symbolic': {
                    'max_steps': 100,
                    'timeout': 30,
                    'proof_format': 'lean',
                    'verification_mode': 'strict'
                }
            }
        }
        
        # Create test theorems and proofs
        self.test_theorems = [
            {
                'id': 'test_1',
                'statement': 'For all real numbers x and y, if x > 0 and y > 0, then xy > 0',
                'domain': 'algebra',
                'difficulty': 'easy',
                'prerequisites': ['Properties of real numbers'],
                'proof': 'Let x and y be positive real numbers. Since x > 0, y > 0, their product xy > 0. [QED]'
            },
            {
                'id': 'test_2',
                'statement': 'The sum of two even numbers is even',
                'domain': 'number_theory',
                'difficulty': 'easy',
                'prerequisites': ['Definition of even numbers'],
                'proof': 'Let a and b be even numbers. Then a = 2k and b = 2m for some integers k, m. '
                        'Their sum a + b = 2k + 2m = 2(k + m) is even. [QED]'
            }
        ]
        
        self.generated_proofs = [
            'Let x and y be positive real numbers. Since x > 0 and y > 0, by the properties of '
            'multiplication of positive numbers, their product xy > 0. [QED]',
            'Let a and b be even numbers. Then a = 2k and b = 2m where k, m are integers. '
            'Therefore, a + b = 2k + 2m = 2(k + m), which is even. [QED]'
        ]
        
        self.reference_proofs = [theorem['proof'] for theorem in self.test_theorems]
        
        # Initialize symbolic reasoner
        self.symbolic_reasoner = SymbolicReasoner(self.config)
        
    def test_text_similarity_metrics(self):
        """Test text similarity metrics calculation"""
        metrics = evaluate_proof_metrics(self.generated_proofs, self.reference_proofs)
        
        # Check metric presence
        self.assertIn('bleu', metrics)
        self.assertIn('rouge1', metrics)
        self.assertIn('rouge2', metrics)
        self.assertIn('rougeL', metrics)
        
        # Check metric values
        for metric_name, metric_value in metrics.items():
            self.assertIsInstance(metric_value, float)
            self.assertGreaterEqual(metric_value, 0)
            self.assertLessEqual(metric_value, 1)
            
    def test_proof_correctness_metrics(self):
        """Test proof correctness metrics calculation"""
        metrics = evaluate_proof_correctness(
            self.symbolic_reasoner,
            self.test_theorems,
            self.generated_proofs
        )
        
        # Check metric presence
        self.assertIn('completeness', metrics)
        self.assertIn('correctness', metrics)
        self.assertIn('efficiency', metrics)
        
        # Check metric values
        for metric_name, metric_value in metrics.items():
            self.assertIsInstance(metric_value, float)
            self.assertGreaterEqual(metric_value, 0)
            self.assertLessEqual(metric_value, 1)
            
    def test_empty_proofs(self):
        """Test metrics calculation with empty proofs"""
        empty_proofs = ['', '']
        
        # Test text similarity metrics
        metrics = evaluate_proof_metrics(empty_proofs, self.reference_proofs)
        self.assertEqual(metrics['bleu'], 0)
        self.assertEqual(metrics['rouge1'], 0)
        
        # Test correctness metrics
        metrics = evaluate_proof_correctness(
            self.symbolic_reasoner,
            self.test_theorems,
            empty_proofs
        )
        self.assertEqual(metrics['completeness'], 0)
        self.assertEqual(metrics['correctness'], 0)
        
    def test_perfect_match(self):
        """Test metrics calculation with perfect matches"""
        # Test text similarity metrics
        metrics = evaluate_proof_metrics(
            self.reference_proofs,
            self.reference_proofs
        )
        self.assertAlmostEqual(metrics['bleu'], 1.0)
        self.assertAlmostEqual(metrics['rouge1'], 1.0)
        
    def test_invalid_input(self):
        """Test metrics calculation with invalid input"""
        # Test with mismatched lengths
        with self.assertRaises(ValueError):
            evaluate_proof_metrics(
                self.generated_proofs[:1],
                self.reference_proofs
            )
            
        with self.assertRaises(ValueError):
            evaluate_proof_correctness(
                self.symbolic_reasoner,
                self.test_theorems,
                self.generated_proofs[:1]
            )
            
    def test_metric_consistency(self):
        """Test consistency of metric calculations"""
        # Calculate metrics multiple times
        metrics1 = evaluate_proof_metrics(
            self.generated_proofs,
            self.reference_proofs
        )
        metrics2 = evaluate_proof_metrics(
            self.generated_proofs,
            self.reference_proofs
        )
        
        # Check if results are consistent
        for metric_name in metrics1:
            self.assertEqual(metrics1[metric_name], metrics2[metric_name])
            
    def test_metric_sensitivity(self):
        """Test sensitivity of metrics to changes"""
        # Create slightly modified proofs
        modified_proofs = [
            proof.replace('positive', 'non-negative')
            for proof in self.generated_proofs
        ]
        
        # Calculate metrics for original and modified proofs
        metrics1 = evaluate_proof_metrics(
            self.generated_proofs,
            self.reference_proofs
        )
        metrics2 = evaluate_proof_metrics(
            modified_proofs,
            self.reference_proofs
        )
        
        # Check if metrics detect the changes
        self.assertNotEqual(metrics1['bleu'], metrics2['bleu'])
        self.assertNotEqual(metrics1['rouge1'], metrics2['rouge1'])
        
if __name__ == '__main__':
    unittest.main() 