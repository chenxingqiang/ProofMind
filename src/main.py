"""
Main entry point for the theorem proving system.
"""
import os
import yaml
import logging
from typing import Dict, Any

from .models.llm_model import GPTInterface
from .symbolic.reasoning_engine import SymbolicReasoner
from .core.proof_generator import HybridProofGenerator
from .core.theorem_prover import HybridTheoremProver
from .data.data_loader import TheoremDataLoader

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    # Expand environment variables in config
    if "llm" in config and "providers" in config["llm"]:
        for provider in config["llm"]["providers"].values():
            if "api_key" in provider and isinstance(provider["api_key"], str):
                if provider["api_key"].startswith("${") and provider["api_key"].endswith("}"):
                    env_var = provider["api_key"][2:-1]
                    provider["api_key"] = os.getenv(env_var)
    
    return config

def setup_logging(config: Dict[str, Any]) -> None:
    """Set up logging configuration.
    
    Args:
        config: Configuration dictionary
    """
    logging_config = config["logging"]
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(logging_config["file"]), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config["level"]),
        format=logging_config["format"],
        handlers=[
            logging.FileHandler(logging_config["file"]),
            logging.StreamHandler()
        ]
    )

def create_theorem_prover(config: Dict[str, Any]) -> HybridTheoremProver:
    """Create and initialize the theorem prover.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized theorem prover
    """
    # Get LLM configuration
    llm_config = config["llm"]
    provider_name = llm_config.get("default_provider", "openai")
    provider_config = llm_config["providers"][provider_name]
    
    # Validate API key
    if not provider_config.get("api_key"):
        raise ValueError(f"API key not found for provider {provider_name}. Please set {provider_name.upper()}_API_KEY environment variable.")
    
    # Initialize components
    llm = GPTInterface(
        provider_name=provider_name,
        config=provider_config
    )
    
    verifier = SymbolicReasoner()
    
    generator = HybridProofGenerator(llm, verifier)
    
    # Create theorem prover
    prover = HybridTheoremProver(generator, verifier)
    
    return prover

def main():
    """Main entry point."""
    try:
        # Load configuration
        config = load_config("config/config.yaml")
        
        # Set up logging
        setup_logging(config)
        
        # Create theorem prover
        prover = create_theorem_prover(config)
        
        # Load example theorems
        data_loader = TheoremDataLoader()
        theorems = data_loader.load_theorems()
        proofs = data_loader.load_proofs()
        
        # Try proving each theorem
        for theorem_id, theorem_data in theorems.items():
            theorem = theorem_data["statement"]
            logging.info(f"\nAttempting to prove theorem {theorem_id}: {theorem}")
            
            # Try to prove the theorem
            result = prover.prove(theorem)
            
            if result["success"]:
                logging.info("✓ Proof successful!")
                logging.info("Proof steps:")
                for i, step in enumerate(result["proof"], 1):
                    logging.info(f"{i}. {step}")
                
                # Compare with example proof if available
                if theorem_id in proofs:
                    example_proof = proofs[theorem_id]
                    logging.info("\nComparing with example proof:")
                    logging.info("Example proof steps:")
                    for i, step in enumerate(example_proof, 1):
                        logging.info(f"{i}. {step}")
            else:
                logging.error(f"✗ Proof failed: {result['error']}")
                if "partial_proof" in result and result["partial_proof"]:
                    logging.info("Partial proof steps:")
                    for i, step in enumerate(result["partial_proof"], 1):
                        logging.info(f"{i}. {step}")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
