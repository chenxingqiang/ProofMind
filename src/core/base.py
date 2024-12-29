"""
Base classes for the theorem proving framework.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class TheoremProver(ABC):
    """Abstract base class for theorem provers."""
    
    @abstractmethod
    def prove(self, theorem: str) -> Dict[str, Any]:
        """Prove a given theorem.
        
        Args:
            theorem: The theorem to prove in string format
            
        Returns:
            Dictionary containing proof details and verification results
        """
        pass

class ProofGenerator(ABC):
    """Abstract base class for proof generators."""
    
    @abstractmethod
    def generate_proof(self, theorem: str) -> List[str]:
        """Generate a proof for a given theorem.
        
        Args:
            theorem: The theorem to prove
            
        Returns:
            List of proof steps
        """
        pass

class ProofVerifier(ABC):
    """Abstract base class for proof verifiers."""
    
    @abstractmethod
    def verify_proof(self, theorem: str, proof: List[str]) -> Dict[str, Any]:
        """Verify a proof for a given theorem.
        
        Args:
            theorem: The theorem being proved
            proof: List of proof steps
            
        Returns:
            Dictionary containing verification results
        """
        pass

class LLMInterface(ABC):
    """Abstract base class for LLM interfaces."""
    
    @abstractmethod
    def generate_strategy(self, theorem: str) -> Dict[str, Any]:
        """Generate a proof strategy using LLM.
        
        Args:
            theorem: The theorem to generate strategy for
            
        Returns:
            Dictionary containing strategy details
        """
        pass
    
    @abstractmethod
    def refine_proof(self, theorem: str, proof: List[str], feedback: Dict[str, Any]) -> List[str]:
        """Refine a proof based on verification feedback.
        
        Args:
            theorem: The theorem being proved
            proof: Current proof steps
            feedback: Verification feedback
            
        Returns:
            Refined proof steps
        """
        pass 