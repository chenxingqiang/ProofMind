"""
Data loader for theorems and proofs.
"""
import os
import json
from typing import Dict, Any, List

class TheoremDataLoader:
    """Loader for theorem and proof data."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        
    def load_theorems(self) -> Dict[str, Any]:
        """Load theorems from JSON file.
        
        Returns:
            Dictionary mapping theorem IDs to theorem data
        """
        theorems_path = os.path.join(self.data_dir, "example_theorems.json")
        
        try:
            with open(theorems_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create example theorems if file doesn't exist
            theorems = {
                "thm1": {
                    "statement": "∀n∈ℕ (n² ≥ n)",
                    "domain": "number_theory",
                    "difficulty": "easy",
                    "prerequisites": [],
                    "description": "For any natural number, its square is greater than or equal to itself."
                },
                "thm2": {
                    "statement": "∀x,y∈ℝ (x > 0 ∧ y > 0 ⟹ xy > 0)",
                    "domain": "algebra",
                    "difficulty": "easy",
                    "prerequisites": ["positivity"],
                    "description": "The product of two positive real numbers is positive."
                },
                "thm3": {
                    "statement": "∀n∈ℕ (n > 1 ⟹ ∃p (p|n ∧ isPrime(p)))",
                    "domain": "number_theory",
                    "difficulty": "medium",
                    "prerequisites": ["prime_numbers", "divisibility"],
                    "description": "Every natural number greater than 1 has a prime factor."
                }
            }
            
            # Save example theorems
            os.makedirs(self.data_dir, exist_ok=True)
            with open(theorems_path, 'w') as f:
                json.dump(theorems, f, indent=2)
            
            return theorems
    
    def load_proofs(self) -> Dict[str, List[str]]:
        """Load example proofs from JSON file.
        
        Returns:
            Dictionary mapping theorem IDs to lists of proof steps
        """
        proofs_path = os.path.join(self.data_dir, "example_proofs.json")
        
        try:
            with open(proofs_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create example proofs if file doesn't exist
            proofs = {
                "thm1": [
                    "Let n be a natural number.",
                    "For n = 0: 0² = 0 ≥ 0 ✓",
                    "For n = 1: 1² = 1 ≥ 1 ✓",
                    "For n > 1: n² = n × n > n × 1 = n (since n > 1)",
                    "Therefore, by cases, n² ≥ n for all n ∈ ℕ."
                ],
                "thm2": [
                    "Let x, y be positive real numbers.",
                    "By definition, x > 0 and y > 0.",
                    "By properties of real numbers, xy > 0 × 0 = 0.",
                    "Therefore, xy > 0."
                ],
                "thm3": [
                    "Let n > 1 be a natural number.",
                    "If n is prime, then n itself is a prime factor of n.",
                    "If n is composite, let p be the smallest prime factor of n.",
                    "Such a p exists by the well-ordering principle.",
                    "Therefore, every n > 1 has a prime factor."
                ]
            }
            
            # Save example proofs
            os.makedirs(self.data_dir, exist_ok=True)
            with open(proofs_path, 'w') as f:
                json.dump(proofs, f, indent=2)
            
            return proofs
    
    def save_proof(self, theorem_id: str, proof: List[str]) -> None:
        """Save a generated proof.
        
        Args:
            theorem_id: ID of the theorem
            proof: List of proof steps
        """
        proofs = self.load_proofs()
        proofs[theorem_id] = proof
        
        proofs_path = os.path.join(self.data_dir, "example_proofs.json")
        with open(proofs_path, 'w') as f:
            json.dump(proofs, f, indent=2)
