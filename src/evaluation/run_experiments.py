import argparse
import yaml
import logging
import os
from pathlib import Path
from typing import Dict, List
from torch.utils.data import DataLoader
from .research_utils import AblationConfig, AblationStudy
from .baseline_comparison import BaselineConfig, BaselineComparison
from .analysis import ResultsAnalyzer
from ..models.trainer import TheoremProverTrainer
from ..data.dataset import TheoremDataset

# Set tokenizer parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_experiment_directories(base_dir: str) -> Dict[str, str]:
    """Setup experiment directories
    
    Args:
        base_dir (str): Base directory for experiments
        
    Returns:
        dict: Map of directory names to paths
    """
    dirs = {
        "results": "results",
        "plots": "plots",
        "models": "models",
        "analysis": "analysis"
    }
    
    paths = {}
    base_path = Path(base_dir)
    
    for name, subdir in dirs.items():
        path = base_path / subdir
        path.mkdir(parents=True, exist_ok=True)
        paths[name] = str(path)
        
    return paths

def run_ablation_study(config: dict, exp_dirs: Dict[str, str]):
    """Run ablation study
    
    Args:
        config (dict): Experiment configuration
        exp_dirs (dict): Experiment directories
    """
    logger.info("Starting ablation study...")
    
    # Create base model
    base_model = create_model("theorem_prover", config)
    
    # Create ablation configuration
    ablation_config = AblationConfig(
        base_config=config,
        ablation_components=config['ablation']['components'],
        metrics=config['evaluation']['metrics'],
        num_runs=config['ablation']['num_runs']
    )
    
    # Create and run ablation study
    study = AblationStudy(ablation_config)
    results = study.run_ablation(
        trainer_cls=lambda c: TheoremProverTrainer(
            model=create_model("theorem_prover", c),
            config=c
        ),
        data_loader_fn=lambda c, t: create_dataloaders(c, t)
    )
    
    # Save results
    save_path = Path(exp_dirs['results']) / "ablation_results.json"
    with open(save_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Saved ablation results to {save_path}")

def run_baseline_comparison(config: dict, exp_dirs: Dict[str, str]):
    """Run baseline comparison
    
    Args:
        config (dict): Experiment configuration
        exp_dirs (dict): Experiment directories
    """
    logger.info("Starting baseline comparison...")
    
    # Create baseline configuration
    baseline_config = BaselineConfig(
        baseline_models=config['baselines']['models'],
        metrics=config['evaluation']['metrics'],
        num_runs=config['baselines']['num_runs'],
        cross_validate=config['baselines']['cross_validate'],
        num_folds=config['baselines']['num_folds']
    )
    
    # Create model factories
    model_factories = {
        name: lambda: TheoremProverTrainer(
            model=create_model(name, config),
            config=config
        )
        for name in config['baselines']['models']
    }
    
    # Create dataset
    dataset = TheoremDataset(config=config)
    
    # Create and run comparison
    comparison = BaselineComparison(baseline_config)
    results = comparison.run_comparison(
        model_factories=model_factories,
        dataset=dataset,
        data_loader_fn=lambda d: create_dataloader(d, config)
    )
    
    # Save results
    save_path = Path(exp_dirs['results']) / "baseline_results.json"
    with open(save_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Saved baseline results to {save_path}")

def analyze_results(exp_dirs: Dict[str, str]):
    """Analyze experimental results
    
    Args:
        exp_dirs (dict): Experiment directories
    """
    logger.info("Starting results analysis...")
    
    # Create analyzer
    analyzer = ResultsAnalyzer(exp_dirs['results'])
    
    # Generate summary tables
    tables = analyzer.generate_summary_tables()
    for name, table in tables.items():
        save_path = Path(exp_dirs['analysis']) / f"{name}_summary.csv"
        table.to_csv(save_path, index=False)
        
    # Generate plots
    for exp_name in analyzer.results:
        for metric in analyzer.results[exp_name].get('metrics', []):
            save_path = Path(exp_dirs['plots']) / f"{exp_name}_{metric}.png"
            analyzer.plot_metric_comparison(
                metric=metric,
                experiment=exp_name,
                output_path=str(save_path)
            )
            
    # Calculate effect sizes
    effect_sizes = analyzer.calculate_effect_sizes()
    save_path = Path(exp_dirs['analysis']) / "effect_sizes.json"
    with open(save_path, 'w') as f:
        json.dump(effect_sizes, f, indent=2)
        
    # Generate LaTeX tables
    latex_tables = analyzer.generate_latex_tables()
    for name, latex in latex_tables.items():
        save_path = Path(exp_dirs['analysis']) / f"{name}_table.tex"
        with open(save_path, 'w') as f:
            f.write(latex)
            
    logger.info(f"Saved analysis results to {exp_dirs['analysis']}")

def create_dataloaders(config: dict, tokenizer) -> tuple:
    """Create data loaders
    
    Args:
        config (dict): Configuration
        tokenizer: Model tokenizer (not used anymore as dataset creates its own)
        
    Returns:
        tuple: Training and validation data loaders
    """
    train_dataset = TheoremDataset(
        config=config,
        split='train'
    )
    
    val_dataset = TheoremDataset(
        config=config,
        split='val'
    )
    
    train_loader = create_dataloader(train_dataset, config)
    val_loader = create_dataloader(val_dataset, config)
    
    return train_loader, val_loader

def create_dataloader(dataset, config: dict):
    """Create data loader
    
    Args:
        dataset: Dataset
        config (dict): Configuration
        
    Returns:
        DataLoader: Data loader
    """
    return DataLoader(
        dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=config['system']['num_workers'],
        pin_memory=config['system']['pin_memory']
    )

def create_model(model_name: str, config: dict):
    """Create model instance
    
    Args:
        model_name (str): Name of model
        config (dict): Configuration
        
    Returns:
        Model instance
    """
    if model_name == "theorem_prover":
        from ..models.llm_model import TheoremLLM
        model = TheoremLLM(config)
        return model
    else:
        raise ValueError(f"Unknown model: {model_name}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run research experiments')
    parser.add_argument('--config', type=str, required=True,
                      help='Path to experiment configuration')
    parser.add_argument('--output-dir', type=str, required=True,
                      help='Base directory for experiment outputs')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = load_config(args.config)
    logger.info("Loaded configuration")
    
    # Setup directories
    exp_dirs = setup_experiment_directories(args.output_dir)
    logger.info("Setup experiment directories")
    
    # Run experiments
    if config.get('run_ablation', True):
        run_ablation_study(config, exp_dirs)
        
    if config.get('run_baselines', True):
        run_baseline_comparison(config, exp_dirs)
        
    # Analyze results
    analyze_results(exp_dirs)
    
    logger.info("Experiments completed")

if __name__ == '__main__':
    main() 