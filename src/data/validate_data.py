# src/data/validate_data.py

from typing import Dict, Any, List
import json
import os
from jsonschema import validate, ValidationError

class TheoremDataValidator:
    """Validator for theorem data"""
    
    def __init__(self):
        """Initialize the validator with schema definitions"""
        self.theorem_schema = {
            "type": "object",
            "required": ["id", "name", "statement", "domain"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "statement": {"type": "string"},
                "domain": {"type": "string", "enum": ["algebra", "topology", "number_theory"]},
                "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                "prerequisites": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "proof_outline": {"type": "string"},
                "metadata": {"type": "object"}
            }
        }
    
    def validate_theorem(self, theorem: Dict[str, Any]) -> tuple:
        """Validate a single theorem
        
        Args:
            theorem (dict): Theorem object to validate
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            validate(instance=theorem, schema=self.theorem_schema)
            return True, ""
        except ValidationError as e:
            return False, str(e)
    
    def validate_dataset(self, theorems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate entire dataset
        
        Args:
            theorems (list): List of theorem objects
        Returns:
            dict: Validation results
        """
        results = {
            'valid_count': 0,
            'invalid_count': 0,
            'errors': []
        }
        
        for theorem in theorems:
            is_valid, error = self.validate_theorem(theorem)
            if is_valid:
                results['valid_count'] += 1
            else:
                results['invalid_count'] += 1
                results['errors'].append({
                    'theorem_id': theorem.get('id', 'unknown'),
                    'error': error
                })
        
        return results
    
    def check_data_completeness(self, theorems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check completeness of dataset
        
        Args:
            theorems (list): List of theorem objects
        Returns:
            dict: Completeness metrics
        """
        metrics = {
            'total_theorems': len(theorems),
            'complete_theorems': 0,
            'missing_fields': {},
            'domain_distribution': {},
            'difficulty_distribution': {}
        }
        
        required_fields = ['id', 'name', 'statement', 'domain']
        
        for theorem in theorems:
            # Check required fields
            missing_fields = [field for field in required_fields if not theorem.get(field)]
            if not missing_fields:
                metrics['complete_theorems'] += 1
            
            # Track missing fields
            for field in missing_fields:
                metrics['missing_fields'][field] = metrics['missing_fields'].get(field, 0) + 1
            
            # Track distributions
            domain = theorem.get('domain')
            if domain:
                metrics['domain_distribution'][domain] = metrics['domain_distribution'].get(domain, 0) + 1
            
            difficulty = theorem.get('difficulty')
            if difficulty:
                metrics['difficulty_distribution'][difficulty] = metrics['difficulty_distribution'].get(difficulty, 0) + 1
        
        return metrics
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate theorem data file
        
        Args:
            file_path (str): Path to theorem data file
        Returns:
            dict: Validation results
        """
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
            
        try:
            with open(file_path, 'r') as f:
                theorems = json.load(f)
                
            if not isinstance(theorems, list):
                return {'error': 'File must contain a list of theorems'}
                
            validation_results = self.validate_dataset(theorems)
            completeness_metrics = self.check_data_completeness(theorems)
            
            return {
                'validation': validation_results,
                'completeness': completeness_metrics,
                'file_path': file_path
            }
            
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON format: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
