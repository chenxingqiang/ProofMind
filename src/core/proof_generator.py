"""
Proof generator implementation.
"""
from typing import Dict, List, Any
from ..core.base import ProofGenerator, LLMInterface, ProofVerifier

class HybridProofGenerator(ProofGenerator):
    """Hybrid proof generator combining LLM and symbolic reasoning."""
    
    def __init__(self, llm: LLMInterface, verifier: ProofVerifier):
        """Initialize the proof generator.
        
        Args:
            llm: LLM interface instance
            verifier: Proof verifier instance
        """
        self.llm = llm
        self.verifier = verifier
        
    def generate_proof(self, theorem: str) -> List[str]:
        """Generate a proof for a given theorem.
        
        Args:
            theorem: The theorem to prove
            
        Returns:
            List of proof steps
        """
        # Generate initial proof strategy
        strategy = self.llm.generate_strategy(theorem)
        
        # Initialize proof steps
        proof_steps = []
        
        # Generate and verify each step
        for step_outline in strategy["steps"]:
            # Generate detailed step
            step = self._generate_step(theorem, step_outline, proof_steps)
            
            # Verify step
            verification = self.verifier.verify_proof(theorem, proof_steps + [step])
            
            if verification["is_valid"]:
                # Add valid step to proof
                proof_steps.append(step)
            else:
                # Refine step based on verification feedback
                refined_steps = self.llm.refine_proof(
                    theorem,
                    proof_steps + [step],
                    verification
                )
                
                # Add refined steps
                for refined_step in refined_steps:
                    refined_verification = self.verifier.verify_proof(
                        theorem,
                        proof_steps + [refined_step]
                    )
                    
                    if refined_verification["is_valid"]:
                        proof_steps.append(refined_step)
                        break
        
        return proof_steps
    
    def _generate_step(self, theorem: str, step_outline: str, previous_steps: List[str]) -> str:
        """Generate a detailed proof step.
        
        Args:
            theorem: The theorem being proved
            step_outline: Outline of the step to generate
            previous_steps: List of previous proof steps
            
        Returns:
            Detailed proof step
        """
        # Create messages for step generation
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a mathematical proof assistant. Your task is to generate "
                    "detailed, formal proof steps based on the given theorem and previous steps. "
                    "Each step should be precise and follow logically from the previous steps."
                )
            },
            {
                "role": "user",
                "content": f"""Given the theorem and previous steps, generate a detailed proof step:

Theorem: {theorem}

Previous steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(previous_steps))}

Step outline: {step_outline}

Generate a formal and precise proof step that follows logically from the previous steps."""
            }
        ]
        
        # Generate step using LLM
        response = self.llm._call_gpt(messages)
        
        # Extract and clean up the generated step
        step = response.strip().split("\n")[-1]  # Take last line as the step
        step = step.split(":", 1)[-1].strip()  # Remove any step numbers/prefixes
        
        return step 