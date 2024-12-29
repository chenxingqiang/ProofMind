"""
Dataset module for handling theorem data in PyTorch.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer

from .data_loader import TheoremDataLoader
from .feature_engineering import TheoremFeatureExtractor

logger = logging.getLogger(__name__)

class TheoremDataset(Dataset):
    """PyTorch dataset for theorem data."""
    
    def __init__(self, 
                 config: Dict[str, Any],
                 split: str = 'train',
                 domains: Optional[List[str]] = None):
        """Initialize the dataset.
        
        Args:
            config: Configuration dictionary
            split: Data split ('train', 'val', or 'test')
            domains: List of domains to include (optional)
        """
        self.config = config
        self.split = split
        self.domains = domains
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config['model']['model_name'])
        
        # Set up padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        # Initialize components
        self.data_loader = TheoremDataLoader(config)
        self.feature_extractor = TheoremFeatureExtractor(config)
        
        # Load and process data
        self.theorems = self._load_and_process_data()
        
        logger.info(f"Loaded {len(self.theorems)} theorems for {split} split")
    
    def __len__(self) -> int:
        """Get dataset size."""
        return len(self.theorems)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get dataset item.
        
        Args:
            idx: Item index
            
        Returns:
            Dictionary containing input tensors
        """
        theorem = self.theorems[idx]
        
        # Prepare input text
        input_text = self._prepare_input_text(theorem)
        target_text = self._prepare_target_text(theorem)
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            padding='max_length',
            truncation=True,
            max_length=self.config['model']['max_tokens'],
            return_tensors='pt'
        )
        
        targets = self.tokenizer(
            target_text,
            padding='max_length',
            truncation=True,
            max_length=self.config['model']['max_tokens'],
            return_tensors='pt'
        )
        
        # Extract features
        features = self.feature_extractor.extract_features(theorem)
        
        # Convert features to tensors
        feature_tensors = {
            key: torch.tensor(value, dtype=torch.float32)
            for key, value in features.items()
        }
        
        return {
            'input_ids': inputs['input_ids'].squeeze(0),
            'attention_mask': inputs['attention_mask'].squeeze(0),
            'labels': targets['input_ids'].squeeze(0),
            'features': feature_tensors,
            'theorem_id': theorem['id']
        }
    
    def _load_and_process_data(self) -> List[Dict[str, Any]]:
        """Load and process theorem data."""
        # Load theorems
        theorems = self.data_loader.load_theorems(
            domains=self.domains,
            split=self.split
        )
        
        # Filter by domain if specified
        if self.domains is not None:
            theorems = [t for t in theorems if t['domain'] in self.domains]
        
        return theorems
    
    def _prepare_input_text(self, theorem: Dict[str, Any]) -> str:
        """Prepare input text for model.
        
        Args:
            theorem: Theorem dictionary
            
        Returns:
            Formatted input text
        """
        # Format: [THEOREM] statement [DOMAIN] domain [DIFFICULTY] difficulty
        text_parts = [
            "[THEOREM]",
            theorem['statement'],
            "[DOMAIN]",
            theorem['domain'],
            "[DIFFICULTY]",
            str(theorem.get('difficulty', 'medium'))
        ]
        
        # Add prerequisites if available
        if theorem.get('prerequisites'):
            text_parts.extend([
                "[PREREQUISITES]",
                ", ".join(theorem['prerequisites'])
            ])
        
        return " ".join(text_parts)
    
    def _prepare_target_text(self, theorem: Dict[str, Any]) -> str:
        """Prepare target text for model.
        
        Args:
            theorem: Theorem dictionary
            
        Returns:
            Formatted target text
        """
        # Format: [PROOF] proof [QED]
        return f"[PROOF] {theorem['proof']} [QED]"
    
    def get_domains(self) -> List[str]:
        """Get unique domains in dataset."""
        return list(set(t['domain'] for t in self.theorems))
    
    def get_theorem_by_id(self, theorem_id: str) -> Optional[Dict[str, Any]]:
        """Get theorem by ID.
        
        Args:
            theorem_id: Theorem identifier
            
        Returns:
            Theorem dictionary if found, None otherwise
        """
        for theorem in self.theorems:
            if theorem['id'] == theorem_id:
                return theorem
        return None
    
    def filter_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Filter theorems by domain.
        
        Args:
            domain: Mathematical domain
            
        Returns:
            List of filtered theorems
        """
        return [t for t in self.theorems if t['domain'] == domain]
    
    def filter_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Filter theorems by difficulty.
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            List of filtered theorems
        """
        return [t for t in self.theorems if t.get('difficulty') == difficulty]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_theorems': len(self.theorems),
            'domains': self.get_domains(),
            'domain_distribution': {},
            'difficulty_distribution': {},
            'avg_statement_length': 0,
            'avg_proof_length': 0
        }
        
        # Calculate distributions
        for theorem in self.theorems:
            # Domain stats
            domain = theorem['domain']
            stats['domain_distribution'][domain] = stats['domain_distribution'].get(domain, 0) + 1
            
            # Difficulty stats
            difficulty = theorem.get('difficulty', 'medium')
            stats['difficulty_distribution'][difficulty] = stats['difficulty_distribution'].get(difficulty, 0) + 1
            
            # Length stats
            stats['avg_statement_length'] += len(theorem['statement'].split())
            stats['avg_proof_length'] += len(theorem['proof'].split())
        
        # Normalize distributions
        total = len(self.theorems)
        stats['domain_distribution'] = {k: v/total for k, v in stats['domain_distribution'].items()}
        stats['difficulty_distribution'] = {k: v/total for k, v in stats['difficulty_distribution'].items()}
        
        # Average lengths
        stats['avg_statement_length'] /= total
        stats['avg_proof_length'] /= total
        
        return stats 