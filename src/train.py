import os
import yaml
import logging
import argparse
import torch
from torch.utils.data import DataLoader
from transformers import set_seed
import wandb
from data.dataset import TheoremDataset
from models.trainer import TheoremProverTrainer

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

def setup_environment(config: dict):
    """Setup training environment
    
    Args:
        config (dict): Configuration dictionary
    """
    # Set random seed
    set_seed(config['training']['seed'])
    
    # Setup CUDA devices
    if torch.cuda.is_available():
        os.environ['CUDA_VISIBLE_DEVICES'] = config['system']['cuda_visible_devices']
        torch.backends.cudnn.deterministic = config['system']['deterministic']
        torch.backends.cudnn.benchmark = config['system']['benchmark']
        
    # Create necessary directories
    os.makedirs(config['training']['save_dir'], exist_ok=True)
    os.makedirs(config['logging']['save_path'], exist_ok=True)
    if config['logging']['use_tensorboard']:
        os.makedirs(config['logging']['tensorboard_dir'], exist_ok=True)
    if config['evaluation']['generate']['save_results']:
        os.makedirs(config['evaluation']['generate']['output_dir'], exist_ok=True)

def create_dataloaders(config: dict, tokenizer) -> tuple:
    """Create training and validation dataloaders
    
    Args:
        config (dict): Configuration dictionary
        tokenizer: Model tokenizer
        
    Returns:
        tuple: Training and validation dataloaders
    """
    # Create datasets
    train_dataset = TheoremDataset(
        config=config,
        tokenizer=tokenizer,
        split='train'
    )
    
    val_dataset = TheoremDataset(
        config=config,
        tokenizer=tokenizer,
        split='val'
    )
    
    logger.info(f"Training dataset size: {len(train_dataset)}")
    logger.info(f"Validation dataset size: {len(val_dataset)}")
    
    # Create dataloaders
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=config['system']['num_workers'],
        pin_memory=config['system']['pin_memory']
    )
    
    val_dataloader = DataLoader(
        val_dataset,
        batch_size=config['training']['val_batch_size'],
        shuffle=False,
        num_workers=config['system']['num_workers'],
        pin_memory=config['system']['pin_memory']
    )
    
    return train_dataloader, val_dataloader

def main():
    """Main training function"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Train theorem proving model')
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                      help='Path to configuration file')
    parser.add_argument('--checkpoint', type=str, default=None,
                      help='Path to checkpoint to resume from')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    logger.info("Loaded configuration")
    
    # Setup environment
    setup_environment(config)
    logger.info("Setup training environment")
    
    # Initialize trainer
    trainer = TheoremProverTrainer(config)
    logger.info("Initialized trainer")
    
    # Load checkpoint if specified
    if args.checkpoint:
        trainer.load_checkpoint(args.checkpoint)
        logger.info(f"Loaded checkpoint from {args.checkpoint}")
    
    # Create dataloaders
    train_dataloader, val_dataloader = create_dataloaders(
        config,
        trainer.model.tokenizer
    )
    logger.info("Created dataloaders")
    
    # Start training
    logger.info("Starting training")
    trainer.train(
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader
    )
    
    logger.info("Training completed")
    
    # Close wandb run if used
    if config['training']['use_wandb']:
        wandb.finish()

if __name__ == '__main__':
    main() 