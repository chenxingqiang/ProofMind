"""
Common utility functions for the theorem proving framework.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

def setup_logging(config: Dict[str, Any]) -> None:
    """Set up logging configuration.
    
    Args:
        config: Logging configuration dictionary
    """
    log_dir = Path(config["file"]).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config["level"]),
        format=config["format"],
        handlers=[
            logging.FileHandler(config["file"]),
            logging.StreamHandler()
        ]
    )

def parse_mathematical_expression(expr: str) -> Tuple[str, List[str], List[str]]:
    """Parse a mathematical expression into its components.
    
    Args:
        expr: Mathematical expression string
        
    Returns:
        Tuple containing:
        - The main operator
        - List of variables
        - List of constants
    """
    # Extract variables (single letters followed by optional subscripts)
    variables = re.findall(r'[a-zA-Z](?:_[0-9]+)?', expr)
    
    # Extract constants (numbers)
    constants = re.findall(r'\d+(?:\.\d+)?', expr)
    
    # Find main operator
    operators = re.findall(r'[+\-*/=<>≤≥∈∀∃∧∨⟹⟺]', expr)
    main_operator = operators[0] if operators else ''
    
    return main_operator, variables, constants

def format_proof_step(step: str, indent: int = 0) -> str:
    """Format a proof step with proper indentation and symbols.
    
    Args:
        step: Proof step text
        indent: Number of spaces to indent
        
    Returns:
        Formatted proof step
    """
    # Replace common mathematical symbols with Unicode
    replacements = {
        '>=': '≥',
        '<=': '≤',
        '=>': '⟹',
        '<=>': '⟺',
        'in': '∈',
        'forall': '∀',
        'exists': '∃',
        'and': '∧',
        'or': '∨',
        'sqrt': '√',
        '^2': '²',
        '^3': '³'
    }
    
    formatted = step
    for old, new in replacements.items():
        formatted = formatted.replace(old, new)
    
    return ' ' * indent + formatted

def validate_proof_structure(proof: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate the structure of a proof.
    
    Args:
        proof: List of proof steps
        
    Returns:
        Tuple containing:
        - Boolean indicating if proof is valid
        - Error message if invalid, None otherwise
    """
    if not proof:
        return False, "Proof is empty"
    
    # Check for common structural elements
    has_assumption = any('let' in step.lower() or 'assume' in step.lower() 
                        for step in proof)
    has_conclusion = any('therefore' in step.lower() or 'thus' in step.lower() 
                        or 'hence' in step.lower() for step in proof)
    
    if not has_assumption:
        return False, "Proof lacks clear assumptions"
    if not has_conclusion:
        return False, "Proof lacks clear conclusion"
    
    return True, None

def extract_theorem_components(theorem: str) -> Dict[str, Any]:
    """Extract components from a theorem statement.
    
    Args:
        theorem: Theorem statement
        
    Returns:
        Dictionary containing:
        - quantifiers: List of quantifiers
        - variables: List of variables
        - domain: Domain of variables
        - hypothesis: Hypothesis statement
        - conclusion: Conclusion statement
    """
    components = {
        'quantifiers': [],
        'variables': [],
        'domain': '',
        'hypothesis': '',
        'conclusion': ''
    }
    
    # Extract quantifiers and variables
    quantifier_matches = re.finditer(r'(∀|∃)([a-zA-Z](?:_[0-9]+)?)', theorem)
    for match in quantifier_matches:
        components['quantifiers'].append(match.group(1))
        components['variables'].append(match.group(2))
    
    # Extract domain
    domain_match = re.search(r'∈\s*([ℕℤℚℝℂ])', theorem)
    if domain_match:
        components['domain'] = domain_match.group(1)
    
    # Split into hypothesis and conclusion
    if '⟹' in theorem:
        parts = theorem.split('⟹')
        components['hypothesis'] = parts[0].strip()
        components['conclusion'] = parts[1].strip()
    elif ',' in theorem:
        # For theorems without explicit implication
        last_comma = theorem.rindex(',')
        components['hypothesis'] = theorem[:last_comma].strip()
        components['conclusion'] = theorem[last_comma + 1:].strip()
    
    return components

def simplify_expression(expr: str) -> str:
    """Simplify a mathematical expression.
    
    Args:
        expr: Mathematical expression
        
    Returns:
        Simplified expression
    """
    # Replace complex expressions with simpler ones
    simplifications = {
        r'x\s*\*\s*1': 'x',
        r'x\s*\+\s*0': 'x',
        r'x\s*-\s*0': 'x',
        r'1\s*\*\s*x': 'x',
        r'0\s*\+\s*x': 'x',
        r'x\s*\^1': 'x',
        r'x\s*\*\s*x': 'x²'
    }
    
    result = expr
    for pattern, replacement in simplifications.items():
        result = re.sub(pattern, replacement, result)
    
    return result

def format_error_message(error: Exception, context: str = '') -> str:
    """Format an error message with context.
    
    Args:
        error: Exception object
        context: Additional context for the error
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"{error_type} in {context}: {error_msg}"
    return f"{error_type}: {error_msg}" 