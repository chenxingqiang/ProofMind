import os
import yaml
import json
import logging
import argparse
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from typing import Dict, List
import numpy as np
from nltk.translate.bleu_score import corpus_bleu
from rouge_score import rouge_scorer
from data.dataset import TheoremDataset
from models.trainer import TheoremProverTrainer
from symbolic.reasoning_engine import SymbolicReasoner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file
    
    Args:
        config_path (str): Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def create_test_dataloader(config: dict, tokenizer) -> DataLoader:
    """Create test dataloader
    
    Args:
        config (dict): Configuration dictionary
        tokenizer: Model tokenizer
        
    Returns:
        DataLoader: Test dataloader
    """
    test_dataset = TheoremDataset(
        config=config,
        tokenizer=tokenizer,
        split='test'
    )
    
    logger.info(f"Test dataset size: {len(test_dataset)}")
    
    return DataLoader(
        test_dataset,
        batch_size=config['training']['val_batch_size'],
        shuffle=False,
        num_workers=config['system']['num_workers'],
        pin_memory=config['system']['pin_memory']
    )

def evaluate_proof_metrics(generated_proofs: List[str],
                         reference_proofs: List[str]) -> Dict[str, float]:
    """Evaluate proof generation metrics
    
    Args:
        generated_proofs (list): Generated proofs
        reference_proofs (list): Reference proofs
        
    Returns:
        dict: Evaluation metrics
    """
    # Calculate BLEU score
    references = [[ref.split()] for ref in reference_proofs]
    candidates = [gen.split() for gen in generated_proofs]
    bleu_score = corpus_bleu(references, candidates)
    
    # Calculate ROUGE scores
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    rouge_scores = {
        'rouge1': 0.0,
        'rouge2': 0.0,
        'rougeL': 0.0
    }
    
    for gen, ref in zip(generated_proofs, reference_proofs):
        scores = scorer.score(ref, gen)
        for key in rouge_scores:
            rouge_scores[key] += scores[key].fmeasure
            
    # Average ROUGE scores
    for key in rouge_scores:
        rouge_scores[key] /= len(generated_proofs)
    
    return {
        'bleu': bleu_score,
        **rouge_scores
    }

def evaluate_proof_correctness(symbolic_reasoner: SymbolicReasoner,
                             theorems: List[Dict],
                             generated_proofs: List[str]) -> Dict[str, float]:
    """Evaluate proof correctness using symbolic reasoner
    
    Args:
        symbolic_reasoner (SymbolicReasoner): Symbolic reasoning engine
        theorems (list): List of theorem dictionaries
        generated_proofs (list): Generated proofs
        
    Returns:
        dict: Correctness metrics
    """
    total_complete = 0
    total_correct = 0
    total_efficient = 0
    
    for theorem, proof in zip(theorems, generated_proofs):
        # Verify proof
        verification_result = symbolic_reasoner.verify_proof(theorem, proof)
        
        # Update metrics
        if verification_result['complete']:
            total_complete += 1
        if verification_result['correct']:
            total_correct += 1
        if verification_result['efficient']:
            total_efficient += 1
            
    num_proofs = len(theorems)
    return {
        'completeness': total_complete / num_proofs,
        'correctness': total_correct / num_proofs,
        'efficiency': total_efficient / num_proofs
    }

def evaluate_model(model: TheoremProverTrainer,
                  test_dataloader: DataLoader,
                  config: dict) -> Dict[str, float]:
    """Evaluate model on test set
    
    Args:
        model (TheoremProverTrainer): Trained model
        test_dataloader (DataLoader): Test dataloader
        config (dict): Configuration dictionary
        
    Returns:
        dict: Evaluation metrics
    """
    model.model.eval()
    symbolic_reasoner = SymbolicReasoner(config)
    
    all_theorems = []
    generated_proofs = []
    reference_proofs = []
    
    logger.info("Generating proofs...")
    with torch.no_grad():
        for batch in tqdm(test_dataloader):
            # Get theorems from batch
            theorems = [
                test_dataloader.dataset.get_theorem_by_id(theorem_id)
                for theorem_id in batch['theorem_id']
            ]
            all_theorems.extend(theorems)
            
            # Generate proofs
            for theorem in theorems:
                proof = model.model.generate_proof(theorem)
                generated_proofs.append(proof)
                if 'proof' in theorem:
                    reference_proofs.append(theorem['proof'])
                    
    # Calculate metrics
    metrics = {}
    
    # Text similarity metrics
    if reference_proofs:
        logger.info("Calculating text similarity metrics...")
        text_metrics = evaluate_proof_metrics(generated_proofs, reference_proofs)
        metrics.update(text_metrics)
    
    # Proof correctness metrics
    logger.info("Evaluating proof correctness...")
    correctness_metrics = evaluate_proof_correctness(
        symbolic_reasoner,
        all_theorems,
        generated_proofs
    )
    metrics.update(correctness_metrics)
    
    # Save results if configured
    if config['evaluation']['generate']['save_results']:
        results = {
            'theorems': all_theorems,
            'generated_proofs': generated_proofs,
            'reference_proofs': reference_proofs,
            'metrics': metrics
        }
        
        output_path = os.path.join(
            config['evaluation']['generate']['output_dir'],
            'evaluation_results.json'
        )
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Saved evaluation results to {output_path}")
    
    return metrics

def main():
    """Main evaluation function"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Evaluate theorem proving model')
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                      help='Path to configuration file')
    parser.add_argument('--checkpoint', type=str, required=True,
                      help='Path to model checkpoint')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    logger.info("Loaded configuration")
    
    # Initialize model and load checkpoint
    model = TheoremProverTrainer(config)
    model.load_checkpoint(args.checkpoint)
    logger.info(f"Loaded checkpoint from {args.checkpoint}")
    
    # Create test dataloader
    test_dataloader = create_test_dataloader(config, model.model.tokenizer)
    logger.info("Created test dataloader")
    
    # Evaluate model
    logger.info("Starting evaluation")
    metrics = evaluate_model(model, test_dataloader, config)
    
    # Print metrics
    logger.info("Evaluation metrics:")
    for metric_name, metric_value in metrics.items():
        logger.info(f"{metric_name}: {metric_value:.4f}")

if __name__ == '__main__':
    main() 