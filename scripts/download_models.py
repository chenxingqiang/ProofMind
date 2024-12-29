#!/usr/bin/env python3
"""
Script to download required models for ProofMind.
This includes the LLM model, tokenizer, and spaCy model for text processing.
"""

import argparse
import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

import torch
from transformers import AutoModel, AutoTokenizer
import spacy
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

def create_model_directory(base_path: str) -> str:
    """Create directory for storing models if it doesn't exist."""
    model_dir = os.path.join(base_path, 'models')
    os.makedirs(model_dir, exist_ok=True)
    return model_dir

def download_llm_model(config: Dict[str, Any], model_dir: str) -> None:
    """Download the LLM model and tokenizer."""
    try:
        model_name = config['model']['type']
        logger.info(f"Downloading model: {model_name}")
        
        # Download and save model
        model = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Add special tokens if specified
        if 'special_tokens' in config['model']:
            special_tokens = config['model']['special_tokens']
            tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
            model.resize_token_embeddings(len(tokenizer))
        
        # Save model and tokenizer
        model_path = os.path.join(model_dir, 'llm')
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
        
        logger.info(f"Successfully saved model and tokenizer to {model_path}")
    except Exception as e:
        logger.error(f"Error downloading LLM model: {e}")
        sys.exit(1)

def download_spacy_model(model_name: str = 'en_core_web_sm') -> None:
    """Download spaCy model for text processing."""
    try:
        logger.info(f"Downloading spaCy model: {model_name}")
        spacy.cli.download(model_name)
        logger.info("Successfully downloaded spaCy model")
    except Exception as e:
        logger.error(f"Error downloading spaCy model: {e}")
        sys.exit(1)

def verify_downloads(model_dir: str, config: Dict[str, Any]) -> None:
    """Verify that all required models were downloaded successfully."""
    try:
        # Check LLM model files
        llm_path = os.path.join(model_dir, 'llm')
        required_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
        
        for file in required_files:
            file_path = os.path.join(llm_path, file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Missing required file: {file_path}")
        
        # Verify spaCy model
        spacy.load('en_core_web_sm')
        
        logger.info("All model files verified successfully")
    except Exception as e:
        logger.error(f"Error verifying downloads: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download required models for ProofMind")
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                      help='Path to configuration file')
    parser.add_argument('--base_path', type=str, default='.',
                      help='Base path for storing models')
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)
        
        # Create model directory
        model_dir = create_model_directory(args.base_path)
        
        # Download models
        download_llm_model(config, model_dir)
        download_spacy_model()
        
        # Verify downloads
        verify_downloads(model_dir, config)
        
        logger.info("Model download completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 