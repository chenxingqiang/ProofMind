import numpy as np
from sklearn.model_selection import KFold
from typing import Dict, List, Optional, Callable
import logging
from dataclasses import dataclass
from .research_utils import calculate_significance, save_experiment_results

logger = logging.getLogger(__name__)

@dataclass
class BaselineConfig:
    """Configuration for baseline comparison"""
    baseline_models: List[str]  # List of baseline model names
    metrics: List[str]  # Metrics to compare
    num_runs: int = 3  # Number of runs per model
    cross_validate: bool = False  # Whether to use cross-validation
    num_folds: int = 5  # Number of CV folds if cross_validate is True

class BaselineComparison:
    """Handles baseline model comparisons"""
    
    def __init__(self, config: BaselineConfig):
        self.config = config
        self.results = {}
        
    def run_comparison(self,
                      model_factories: Dict[str, Callable],
                      dataset,
                      data_loader_fn) -> Dict:
        """Run baseline comparison
        
        Args:
            model_factories (dict): Map of model name to model factory function
            dataset: Dataset to use
            data_loader_fn: Function to create data loader
            
        Returns:
            dict: Comparison results
        """
        if self.config.cross_validate:
            return self._run_cross_validation(model_factories, dataset, data_loader_fn)
        else:
            return self._run_direct_comparison(model_factories, dataset, data_loader_fn)
    
    def _run_direct_comparison(self,
                             model_factories: Dict[str, Callable],
                             dataset,
                             data_loader_fn) -> Dict:
        """Run direct comparison between models
        
        Args:
            model_factories (dict): Map of model name to model factory function
            dataset: Dataset to use
            data_loader_fn: Function to create data loader
            
        Returns:
            dict: Comparison results
        """
        for model_name in self.config.baseline_models:
            logger.info(f"Evaluating {model_name}...")
            model_factory = model_factories[model_name]
            model_results = defaultdict(list)
            
            for run in range(self.config.num_runs):
                logger.info(f"Run {run + 1}/{self.config.num_runs}")
                
                # Create and train model
                model = model_factory()
                train_loader, val_loader = data_loader_fn(dataset)
                model.train(train_loader)
                
                # Evaluate
                metrics = model.evaluate(val_loader)
                for metric in self.config.metrics:
                    if metric in metrics:
                        model_results[metric].append(metrics[metric])
            
            self.results[model_name] = model_results
            
        return self._analyze_results()
    
    def _run_cross_validation(self,
                            model_factories: Dict[str, Callable],
                            dataset,
                            data_loader_fn) -> Dict:
        """Run cross-validation comparison
        
        Args:
            model_factories (dict): Map of model name to model factory function
            dataset: Dataset to use
            data_loader_fn: Function to create data loader
            
        Returns:
            dict: Cross-validation results
        """
        kf = KFold(n_splits=self.config.num_folds, shuffle=True)
        
        for model_name in self.config.baseline_models:
            logger.info(f"Cross-validating {model_name}...")
            model_factory = model_factories[model_name]
            model_results = defaultdict(list)
            
            for fold, (train_idx, val_idx) in enumerate(kf.split(dataset)):
                logger.info(f"Fold {fold + 1}/{self.config.num_folds}")
                
                # Split dataset
                train_data = dataset[train_idx]
                val_data = dataset[val_idx]
                
                # Create and train model
                model = model_factory()
                train_loader = data_loader_fn(train_data)
                val_loader = data_loader_fn(val_data)
                model.train(train_loader)
                
                # Evaluate
                metrics = model.evaluate(val_loader)
                for metric in self.config.metrics:
                    if metric in metrics:
                        model_results[metric].append(metrics[metric])
            
            self.results[model_name] = model_results
            
        return self._analyze_cross_validation()
    
    def _analyze_results(self) -> Dict:
        """Analyze comparison results
        
        Returns:
            dict: Analysis results
        """
        analysis = {}
        
        # Calculate statistics for each model
        for model_name, model_results in self.results.items():
            model_analysis = {}
            
            for metric in self.config.metrics:
                values = model_results[metric]
                model_analysis[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values)
                }
            
            analysis[model_name] = model_analysis
            
        # Calculate significance between pairs of models
        significance_tests = {}
        models = list(self.results.keys())
        
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                model_a = models[i]
                model_b = models[j]
                
                pair_tests = {}
                for metric in self.config.metrics:
                    results_a = self.results[model_a][metric]
                    results_b = self.results[model_b][metric]
                    
                    t_stat, p_value = calculate_significance(
                        results_a,
                        results_b,
                        test_type="ttest"
                    )
                    
                    pair_tests[metric] = {
                        "t_statistic": t_stat,
                        "p_value": p_value,
                        "significant": p_value < 0.05
                    }
                
                significance_tests[f"{model_a}_vs_{model_b}"] = pair_tests
                
        analysis["significance_tests"] = significance_tests
        return analysis
    
    def _analyze_cross_validation(self) -> Dict:
        """Analyze cross-validation results
        
        Returns:
            dict: Analysis results
        """
        analysis = {}
        
        # Calculate CV statistics for each model
        for model_name, model_results in self.results.items():
            model_analysis = {}
            
            for metric in self.config.metrics:
                values = model_results[metric]
                model_analysis[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "cv_score": np.mean(values),
                    "cv_std": np.std(values) * np.sqrt(self.config.num_folds)
                }
            
            analysis[model_name] = model_analysis
            
        # Calculate significance between pairs of models
        significance_tests = {}
        models = list(self.results.keys())
        
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                model_a = models[i]
                model_b = models[j]
                
                pair_tests = {}
                for metric in self.config.metrics:
                    results_a = self.results[model_a][metric]
                    results_b = self.results[model_b][metric]
                    
                    # Use paired t-test for CV results
                    t_stat, p_value = calculate_significance(
                        results_a,
                        results_b,
                        test_type="ttest"
                    )
                    
                    pair_tests[metric] = {
                        "t_statistic": t_stat,
                        "p_value": p_value,
                        "significant": p_value < 0.05
                    }
                
                significance_tests[f"{model_a}_vs_{model_b}"] = pair_tests
                
        analysis["significance_tests"] = significance_tests
        return analysis 