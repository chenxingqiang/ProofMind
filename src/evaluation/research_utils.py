import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
import logging
import json
import os
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class AblationConfig:
    """Configuration for ablation studies"""
    base_config: dict  # Base configuration
    ablation_components: List[str]  # Components to ablate
    metrics: List[str]  # Metrics to track
    num_runs: int = 3  # Number of runs per configuration

class AblationStudy:
    """Handles ablation studies for the theorem prover"""
    
    def __init__(self, config: AblationConfig):
        self.config = config
        self.results = defaultdict(list)
        
    def run_ablation(self, trainer_cls, data_loader_fn) -> Dict:
        """Run ablation study
        
        Args:
            trainer_cls: Trainer class to use
            data_loader_fn: Function to create data loaders
            
        Returns:
            dict: Ablation results
        """
        # Run baseline
        logger.info("Running baseline configuration...")
        baseline_results = self._run_configuration(
            self.config.base_config,
            trainer_cls,
            data_loader_fn,
            "baseline"
        )
        
        # Run ablations
        for component in self.config.ablation_components:
            logger.info(f"Running ablation for {component}...")
            ablated_config = self._ablate_component(self.config.base_config, component)
            self._run_configuration(
                ablated_config,
                trainer_cls,
                data_loader_fn,
                component
            )
            
        return self._analyze_results()
    
    def _ablate_component(self, config: dict, component: str) -> dict:
        """Create ablated configuration
        
        Args:
            config (dict): Base configuration
            component (str): Component to ablate
            
        Returns:
            dict: Ablated configuration
        """
        ablated_config = config.copy()
        
        # Handle different ablation types
        if component in ablated_config['model']:
            ablated_config['model'][component] = False
        elif component in ablated_config.get('training', {}):
            ablated_config['training'][component] = False
        elif component in ablated_config.get('data', {}):
            ablated_config['data'][component] = False
            
        return ablated_config
    
    def _run_configuration(self, 
                         config: dict,
                         trainer_cls,
                         data_loader_fn,
                         config_name: str) -> Dict[str, List[float]]:
        """Run multiple trials of a configuration
        
        Args:
            config (dict): Configuration to run
            trainer_cls: Trainer class
            data_loader_fn: Function to create data loaders
            config_name (str): Name of configuration
            
        Returns:
            dict: Results for each metric
        """
        config_results = defaultdict(list)
        
        for run in range(self.config.num_runs):
            logger.info(f"Running trial {run + 1}/{self.config.num_runs}")
            
            # Create trainer and data loaders
            trainer = trainer_cls(config)
            train_loader, val_loader = data_loader_fn(config, trainer.model.tokenizer)
            
            # Train and evaluate
            trainer.train(train_loader, val_loader)
            metrics = trainer.evaluate(val_loader)
            
            # Store results
            for metric in self.config.metrics:
                if metric in metrics:
                    config_results[metric].append(metrics[metric])
                    
        # Store in overall results
        self.results[config_name] = config_results
        return config_results
    
    def _analyze_results(self) -> Dict:
        """Analyze ablation results with statistical tests
        
        Returns:
            dict: Analysis results
        """
        analysis = {}
        baseline_results = self.results["baseline"]
        
        for component in self.config.ablation_components:
            ablated_results = self.results[component]
            component_analysis = {}
            
            for metric in self.config.metrics:
                baseline_values = baseline_results[metric]
                ablated_values = ablated_results[metric]
                
                # Calculate statistics
                t_stat, p_value = stats.ttest_ind(baseline_values, ablated_values)
                
                component_analysis[metric] = {
                    "baseline_mean": np.mean(baseline_values),
                    "baseline_std": np.std(baseline_values),
                    "ablated_mean": np.mean(ablated_values),
                    "ablated_std": np.std(ablated_values),
                    "difference": np.mean(baseline_values) - np.mean(ablated_values),
                    "p_value": p_value,
                    "significant": p_value < 0.05
                }
                
            analysis[component] = component_analysis
            
        return analysis

def calculate_significance(
    results_a: List[float],
    results_b: List[float],
    test_type: str = "ttest"
) -> Tuple[float, float]:
    """Calculate statistical significance between two sets of results
    
    Args:
        results_a (list): First set of results
        results_b (list): Second set of results
        test_type (str): Type of statistical test
        
    Returns:
        tuple: Test statistic and p-value
    """
    if test_type == "ttest":
        return stats.ttest_ind(results_a, results_b)
    elif test_type == "wilcoxon":
        return stats.wilcoxon(results_a, results_b)
    else:
        raise ValueError(f"Unknown test type: {test_type}")

def save_experiment_results(
    results: Dict,
    output_dir: str,
    experiment_name: str
):
    """Save experiment results with proper formatting
    
    Args:
        results (dict): Experiment results
        output_dir (str): Output directory
        experiment_name (str): Name of experiment
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{experiment_name}_results.json")
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved results to {output_path}") 