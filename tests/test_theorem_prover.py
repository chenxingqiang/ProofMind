"""
Test cases for the theorem prover framework.
"""
import pytest
from unittest.mock import Mock, patch

from src.core.theorem_prover import HybridTheoremProver
from src.models.llm_model import GPTInterface
from src.symbolic.reasoning_engine import SymbolicReasoner
from src.core.proof_generator import HybridProofGenerator

@pytest.fixture
def mock_llm():
    """Create a mock LLM interface."""
    llm = Mock(spec=GPTInterface)
    llm.generate_strategy.return_value = {
        "success": True,
        "strategy": [
            "Use proof by induction",
            "Base case: Show true for n=1",
            "Inductive step: Assume true for k, prove for k+1"
        ]
    }
    llm.refine_proof.return_value = {
        "success": True,
        "refined_proof": [
            "Let's prove this by induction.",
            "Base case (n=1): 1² = 1 ≥ 1 ✓",
            "Inductive step: Assume k² ≥ k for some k ≥ 1",
            "Then (k+1)² = k² + 2k + 1 > k² ≥ k > k+1",
            "Therefore, by mathematical induction, n² ≥ n for all n ∈ ℕ"
        ]
    }
    return llm

@pytest.fixture
def mock_verifier():
    """Create a mock symbolic reasoner."""
    verifier = Mock(spec=SymbolicReasoner)
    verifier.verify_proof.return_value = {
        "is_valid": True,
        "verification_steps": [
            "Verified base case: 1² = 1 ≥ 1",
            "Verified inductive hypothesis: k² ≥ k",
            "Verified inductive step: (k+1)² ≥ k+1",
            "Verified conclusion: ∀n∈ℕ (n² ≥ n)"
        ]
    }
    return verifier

@pytest.fixture
def mock_generator(mock_llm, mock_verifier):
    """Create a mock proof generator."""
    generator = Mock(spec=HybridProofGenerator)
    generator.generate_proof.return_value = [
        "Let's prove this by induction.",
        "Base case (n=1): 1² = 1 ≥ 1 ✓",
        "Inductive step: Assume k² ≥ k for some k ≥ 1",
        "Then (k+1)² = k² + 2k + 1 > k² ≥ k > k+1",
        "Therefore, by mathematical induction, n² ≥ n for all n ∈ ℕ"
    ]
    return generator

def test_prove_simple_theorem(mock_generator, mock_verifier):
    """Test proving a simple theorem about natural numbers."""
    # Arrange
    theorem = "∀n∈ℕ (n² ≥ n)"
    prover = HybridTheoremProver(mock_generator, mock_verifier)
    
    # Act
    result = prover.prove(theorem)
    
    # Assert
    assert result["success"] is True
    assert len(result["proof"]) > 0
    assert "Base case" in result["proof"][1]
    assert "Inductive step" in result["proof"][2]
    
    # Verify interactions
    mock_generator.generate_proof.assert_called_once_with(theorem)
    mock_verifier.verify_proof.assert_called_once()

def test_prove_invalid_theorem(mock_generator, mock_verifier):
    """Test proving an invalid theorem."""
    # Arrange
    theorem = "∀n∈ℕ (n < n²)"  # Invalid theorem
    mock_verifier.verify_proof.return_value = {
        "is_valid": False,
        "error": "Counter-example found: n = 0"
    }
    prover = HybridTheoremProver(mock_generator, mock_verifier)
    
    # Act
    result = prover.prove(theorem)
    
    # Assert
    assert result["success"] is False
    assert "Counter-example" in result["error"]
    assert result["partial_proof"] is not None

def test_prove_complex_theorem(mock_generator, mock_verifier):
    """Test proving a more complex theorem."""
    # Arrange
    theorem = "∀x,y∈ℝ (x > 0 ∧ y > 0 ⟹ xy > 0)"
    mock_generator.generate_proof.return_value = [
        "Let x, y be positive real numbers",
        "By definition, x > 0 and y > 0",
        "By properties of real numbers, xy > 0",
        "Therefore, the product of positive numbers is positive"
    ]
    prover = HybridTheoremProver(mock_generator, mock_verifier)
    
    # Act
    result = prover.prove(theorem)
    
    # Assert
    assert result["success"] is True
    assert len(result["proof"]) == 4
    assert "positive real numbers" in result["proof"][0]

def test_prove_with_llm_failure(mock_generator, mock_verifier):
    """Test handling of LLM failure."""
    # Arrange
    theorem = "∀n∈ℕ (n² ≥ n)"
    mock_generator.generate_proof.side_effect = Exception("API error")
    prover = HybridTheoremProver(mock_generator, mock_verifier)
    
    # Act
    result = prover.prove(theorem)
    
    # Assert
    assert result["success"] is False
    assert "API error" in result["error"]
    assert result["partial_proof"] is None

def test_prove_with_verification_timeout(mock_generator, mock_verifier):
    """Test handling of verification timeout."""
    # Arrange
    theorem = "∀n∈ℕ (n² ≥ n)"
    mock_verifier.verify_proof.side_effect = TimeoutError("Verification timeout")
    prover = HybridTheoremProver(mock_generator, mock_verifier)
    
    # Act
    result = prover.prove(theorem)
    
    # Assert
    assert result["success"] is False
    assert "timeout" in result["error"].lower()
    assert result["partial_proof"] is not None 