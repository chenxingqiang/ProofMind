#!/usr/bin/env python3
"""
Script to download and generate sample theorem data for ProofMind.
This includes theorems from various mathematical domains with proofs.
"""

import argparse
import json
import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        sys.exit(1)

def create_data_directories(base_path: str) -> Dict[str, str]:
    """Create directories for storing data."""
    directories = {
        'train': os.path.join(base_path, 'data', 'train'),
        'val': os.path.join(base_path, 'data', 'val'),
        'test': os.path.join(base_path, 'data', 'test')
    }
    
    for directory in directories.values():
        os.makedirs(directory, exist_ok=True)
    
    return directories

def generate_algebra_theorems() -> List[Dict[str, Any]]:
    """Generate sample algebra theorems."""
    return [
        {
            "id": "alg_001",
            "statement": "For all real numbers x and y, if x > 0 and y > 0, then xy > 0",
            "domain": "algebra",
            "difficulty": "easy",
            "prerequisites": [
                "Properties of real numbers",
                "Multiplication of positive numbers"
            ],
            "proof": "Let x and y be positive real numbers. By definition of positive numbers, x > 0 and y > 0. By the properties of multiplication of positive numbers, their product xy is also positive. Therefore, xy > 0."
        },
        {
            "id": "alg_002",
            "statement": "For any real number x, x² ≥ 0",
            "domain": "algebra",
            "difficulty": "easy",
            "prerequisites": [
                "Properties of real numbers",
                "Square of a number"
            ],
            "proof": "Let x be any real number. If x > 0, then x² > 0. If x < 0, then -x > 0, so x² = (-x)² > 0. If x = 0, then x² = 0. Therefore, in all cases, x² ≥ 0."
        }
    ]

def generate_analysis_theorems() -> List[Dict[str, Any]]:
    """Generate sample analysis theorems."""
    return [
        {
            "id": "ana_001",
            "statement": "If f is continuous at a and lim(x→a) g(x) = g(a), then lim(x→a) f(g(x)) = f(g(a))",
            "domain": "analysis",
            "difficulty": "medium",
            "prerequisites": [
                "Continuity",
                "Function composition",
                "Limits"
            ],
            "proof": "Let ε > 0. Since f is continuous at a, there exists δ₁ > 0 such that |y - g(a)| < δ₁ implies |f(y) - f(g(a))| < ε. Since lim(x→a) g(x) = g(a), there exists δ₂ > 0 such that |x - a| < δ₂ implies |g(x) - g(a)| < δ₁. Let δ = δ₂. Then |x - a| < δ implies |f(g(x)) - f(g(a))| < ε. Therefore, lim(x→a) f(g(x)) = f(g(a))."
        }
    ]

def generate_geometry_theorems() -> List[Dict[str, Any]]:
    """Generate sample geometry theorems."""
    return [
        {
            "id": "geo_001",
            "statement": "The sum of the angles in a triangle is 180 degrees",
            "domain": "geometry",
            "difficulty": "easy",
            "prerequisites": [
                "Parallel lines",
                "Angles",
                "Triangle properties"
            ],
            "proof": "Consider a triangle ABC. Draw a line through point A parallel to BC. This creates alternate angles equal to angles B and C. The sum of angles on a straight line is 180 degrees. Therefore, the sum of the angles in triangle ABC is 180 degrees."
        }
    ]

def generate_number_theory_theorems() -> List[Dict[str, Any]]:
    """Generate sample number theory theorems."""
    return [
        {
            "id": "nt_001",
            "statement": "The sum of two even numbers is even",
            "domain": "number_theory",
            "difficulty": "easy",
            "prerequisites": [
                "Even numbers",
                "Integer arithmetic"
            ],
            "proof": "Let a and b be even numbers. Then a = 2k and b = 2m for some integers k and m. The sum a + b = 2k + 2m = 2(k + m). Since k + m is an integer, a + b is even."
        }
    ]

def generate_topology_theorems() -> List[Dict[str, Any]]:
    """Generate sample topology theorems."""
    return [
        {
            "id": "top_001",
            "statement": "The intersection of any finite collection of open sets is open",
            "domain": "topology",
            "difficulty": "medium",
            "prerequisites": [
                "Open sets",
                "Set operations",
                "Topological spaces"
            ],
            "proof": "Let {U₁, ..., Uₙ} be a finite collection of open sets. Let x ∈ ∩ᵢUᵢ. For each i, since Uᵢ is open, there exists rᵢ > 0 such that B(x,rᵢ) ⊆ Uᵢ. Let r = min{rᵢ}. Then B(x,r) ⊆ ∩ᵢUᵢ. Therefore, ∩ᵢUᵢ is open."
        }
    ]

def create_data_splits(theorems: List[Dict[str, Any]], split_ratios: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
    """Split theorems into training, validation, and test sets."""
    total = len(theorems)
    train_size = int(total * split_ratios['train'])
    val_size = int(total * split_ratios['val'])
    
    splits = {
        'train': theorems[:train_size],
        'val': theorems[train_size:train_size + val_size],
        'test': theorems[train_size + val_size:]
    }
    
    return splits

def save_theorems(theorems: List[Dict[str, Any]], directory: str, domain: str) -> None:
    """Save theorems to JSON file."""
    try:
        output_file = os.path.join(directory, f"{domain}_theorems.json")
        with open(output_file, 'w') as f:
            json.dump(theorems, f, indent=2)
        logger.info(f"Saved {len(theorems)} theorems to {output_file}")
    except Exception as e:
        logger.error(f"Error saving theorems: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download sample theorem data for ProofMind")
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                      help='Path to configuration file')
    parser.add_argument('--base_path', type=str, default='.',
                      help='Base path for storing data')
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)
        
        # Create data directories
        directories = create_data_directories(args.base_path)
        
        # Generate theorems for each domain
        theorem_generators = {
            'algebra': generate_algebra_theorems,
            'analysis': generate_analysis_theorems,
            'geometry': generate_geometry_theorems,
            'number_theory': generate_number_theory_theorems,
            'topology': generate_topology_theorems
        }
        
        # Split ratios
        split_ratios = {
            'train': 0.7,
            'val': 0.15,
            'test': 0.15
        }
        
        # Generate and save theorems for each domain
        for domain, generator in tqdm(theorem_generators.items(), desc="Generating theorems"):
            theorems = generator()
            splits = create_data_splits(theorems, split_ratios)
            
            for split_name, split_theorems in splits.items():
                save_theorems(split_theorems, directories[split_name], domain)
        
        logger.info("Sample data generation completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 