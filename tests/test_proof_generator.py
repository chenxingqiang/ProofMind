# tests/test_proof_generator.py

import unittest
from src.proof_generator import ProofGenerator


class TestProofGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ProofGenerator()

    def test_proof_generation(self):
        theorem = {
            'statement': 'For all n > 1, n has a prime factor.'
        }
        proof = self.generator.generate_proofs([theorem])[0]
        self.assertIsNotNone(proof['proof'])
