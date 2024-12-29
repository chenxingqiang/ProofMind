import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import logging
from pathlib import Path
import json
from scipy import stats

logger = logging.getLogger(__name__)

class ResultsAnalyzer:
    """Analyzes and visualizes experimental results"""
    
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
        self.results = {}
        self._load_results()
        
    def _load_results(self):
        """Load results from JSON files"""
        for results_file in self.results_dir.glob("*_results.json"):
            with open(results_file, 'r') as f:
                experiment_name = results_file.stem.replace("_results", "")
                self.results[experiment_name] = json.load(f)
                
    def generate_summary_tables(self) -> Dict[str, pd.DataFrame]:
        """Generate summary tables for all experiments
        
        Returns:
            dict: Map of experiment name to summary DataFrame
        """
        summary_tables = {}
        
        for exp_name, exp_results in self.results.items():
            if "ablation" in exp_name:
                summary_tables[exp_name] = self._summarize_ablation(exp_results)
            elif "baseline" in exp_name:
                summary_tables[exp_name] = self._summarize_baseline(exp_results)
            else:
                summary_tables[exp_name] = self._summarize_general(exp_results)
                
        return summary_tables
    
    def _summarize_ablation(self, results: Dict) -> pd.DataFrame:
        """Create summary table for ablation study
        
        Args:
            results (dict): Ablation study results
            
        Returns:
            DataFrame: Summary table
        """
        rows = []
        
        for component, metrics in results.items():
            if component != "baseline":
                row = {"Component": component}
                
                for metric, values in metrics.items():
                    row[f"{metric}_diff"] = values["difference"]
                    row[f"{metric}_p"] = values["p_value"]
                    row[f"{metric}_sig"] = "✓" if values["significant"] else ""
                    
                rows.append(row)
                
        return pd.DataFrame(rows)
    
    def _summarize_baseline(self, results: Dict) -> pd.DataFrame:
        """Create summary table for baseline comparison
        
        Args:
            results (dict): Baseline comparison results
            
        Returns:
            DataFrame: Summary table
        """
        rows = []
        
        for model, metrics in results.items():
            if model != "significance_tests":
                row = {"Model": model}
                
                for metric, values in metrics.items():
                    row[f"{metric}_mean"] = values["mean"]
                    row[f"{metric}_std"] = values["std"]
                    
                rows.append(row)
                
        return pd.DataFrame(rows)
    
    def _summarize_general(self, results: Dict) -> pd.DataFrame:
        """Create summary table for general results
        
        Args:
            results (dict): General results
            
        Returns:
            DataFrame: Summary table
        """
        if isinstance(results, dict):
            return pd.DataFrame([results])
        return pd.DataFrame(results)
    
    def plot_metric_comparison(self,
                             metric: str,
                             experiment: str,
                             output_path: Optional[str] = None):
        """Plot comparison of a metric across models/components
        
        Args:
            metric (str): Metric to plot
            experiment (str): Experiment name
            output_path (str, optional): Path to save plot
        """
        results = self.results[experiment]
        plt.figure(figsize=(10, 6))
        
        if "ablation" in experiment:
            self._plot_ablation_comparison(results, metric)
        elif "baseline" in experiment:
            self._plot_baseline_comparison(results, metric)
        else:
            self._plot_general_comparison(results, metric)
            
        if output_path:
            plt.savefig(output_path)
        plt.close()
    
    def _plot_ablation_comparison(self, results: Dict, metric: str):
        """Plot ablation study comparison
        
        Args:
            results (dict): Ablation results
            metric (str): Metric to plot
        """
        components = []
        values = []
        errors = []
        
        baseline_mean = results["baseline"][metric]["baseline_mean"]
        plt.axhline(y=baseline_mean, color='r', linestyle='--', label='Baseline')
        
        for component, metrics in results.items():
            if component != "baseline":
                components.append(component)
                values.append(metrics[metric]["ablated_mean"])
                errors.append(metrics[metric]["ablated_std"])
                
        plt.bar(components, values, yerr=errors, capsize=5)
        plt.xticks(rotation=45)
        plt.title(f"Impact of Component Ablation on {metric}")
        plt.ylabel(metric)
        plt.legend()
        
    def _plot_baseline_comparison(self, results: Dict, metric: str):
        """Plot baseline comparison
        
        Args:
            results (dict): Baseline results
            metric (str): Metric to plot
        """
        models = []
        values = []
        errors = []
        
        for model, metrics in results.items():
            if model != "significance_tests":
                models.append(model)
                values.append(metrics[metric]["mean"])
                errors.append(metrics[metric]["std"])
                
        plt.bar(models, values, yerr=errors, capsize=5)
        plt.xticks(rotation=45)
        plt.title(f"Comparison of {metric} Across Models")
        plt.ylabel(metric)
        
    def _plot_general_comparison(self, results: Dict, metric: str):
        """Plot general results comparison
        
        Args:
            results (dict): General results
            metric (str): Metric to plot
        """
        if isinstance(results, dict):
            plt.bar([metric], [results[metric]])
            plt.title(f"{metric} Value")
        else:
            values = [r[metric] for r in results if metric in r]
            plt.hist(values, bins='auto')
            plt.title(f"Distribution of {metric}")
            plt.xlabel(metric)
            plt.ylabel("Frequency")
            
    def generate_latex_tables(self) -> Dict[str, str]:
        """Generate LaTeX tables for paper
        
        Returns:
            dict: Map of table name to LaTeX string
        """
        latex_tables = {}
        summary_tables = self.generate_summary_tables()
        
        for name, df in summary_tables.items():
            latex_tables[name] = df.to_latex(
                index=False,
                float_format=lambda x: '{:.3f}'.format(x) if isinstance(x, float) else x
            )
            
        return latex_tables
    
    def calculate_effect_sizes(self) -> Dict[str, Dict]:
        """Calculate effect sizes for experiments
        
        Returns:
            dict: Effect size calculations
        """
        effect_sizes = {}
        
        for exp_name, results in self.results.items():
            if "baseline" in exp_name:
                effect_sizes[exp_name] = self._calculate_baseline_effects(results)
            elif "ablation" in exp_name:
                effect_sizes[exp_name] = self._calculate_ablation_effects(results)
                
        return effect_sizes
    
    def _calculate_baseline_effects(self, results: Dict) -> Dict:
        """Calculate effect sizes for baseline comparison
        
        Args:
            results (dict): Baseline results
            
        Returns:
            dict: Effect sizes
        """
        effects = {}
        models = [m for m in results.keys() if m != "significance_tests"]
        
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                model_a = models[i]
                model_b = models[j]
                pair_effects = {}
                
                for metric in results[model_a].keys():
                    values_a = np.array(results[model_a][metric])
                    values_b = np.array(results[model_b][metric])
                    
                    # Calculate Cohen's d
                    pooled_std = np.sqrt((np.var(values_a) + np.var(values_b)) / 2)
                    effect_size = (np.mean(values_a) - np.mean(values_b)) / pooled_std
                    
                    pair_effects[metric] = {
                        "cohens_d": effect_size,
                        "magnitude": self._interpret_effect_size(effect_size)
                    }
                    
                effects[f"{model_a}_vs_{model_b}"] = pair_effects
                
        return effects
    
    def _calculate_ablation_effects(self, results: Dict) -> Dict:
        """Calculate effect sizes for ablation study
        
        Args:
            results (dict): Ablation results
            
        Returns:
            dict: Effect sizes
        """
        effects = {}
        baseline_results = results["baseline"]
        
        for component, metrics in results.items():
            if component != "baseline":
                component_effects = {}
                
                for metric in metrics.keys():
                    effect_size = metrics[metric]["difference"] / baseline_results[metric]["baseline_std"]
                    
                    component_effects[metric] = {
                        "cohens_d": effect_size,
                        "magnitude": self._interpret_effect_size(effect_size)
                    }
                    
                effects[component] = component_effects
                
        return effects
    
    @staticmethod
    def _interpret_effect_size(d: float) -> str:
        """Interpret Cohen's d effect size
        
        Args:
            d (float): Effect size
            
        Returns:
            str: Interpretation
        """
        d = abs(d)
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large" 