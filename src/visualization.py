# src/visualization.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List
import json

logger = logging.getLogger(__name__)


def plot_training_history(history: dict, output_path: str):
    """
    绘制训练历史曲线
    
    Args:
        history: 包含训练历史的字典，包含 'train_loss' 和 'val_loss'
        output_path: 输出文件路径
    """
    try:
        plt.figure(figsize=(10, 6))

        # 绘制损失曲线
        epochs = range(1, len(history['train_loss']) + 1)
        plt.plot(epochs, history['train_loss'], 'b-', label='Training Loss')
        plt.plot(epochs, history['val_loss'], 'r-', label='Validation Loss')

        plt.title('Training and Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)

        # 保存图像
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Training history visualization saved to {output_path}")

    except Exception as e:
        logger.error(
            f"Error creating training history visualization: {str(e)}")
        raise


def plot_results(results: dict, output_path: str):
    """
    绘制验证结果
    
    Args:
        results: 验证结果字典
        output_path: 输出文件路径
    """
    try:
        # 创建结果可视化
        plt.figure(figsize=(12, 6))

        # 根据结果类型创建适当的可视化
        if isinstance(results, dict) and 'accuracy' in results:
            plt.bar(['Accuracy'], [results['accuracy']])
            plt.title('Model Performance')
            plt.ylabel('Accuracy')
        else:
            # 如果没有准确率，显示其他可用的指标
            metrics = list(results.items())
            plt.bar([k for k, v in metrics], [v for k, v in metrics])
            plt.title('Model Metrics')
            plt.xticks(rotation=45)

        plt.ylim(0, 1)
        plt.grid(True, axis='y')

        # 保存图像
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Results visualization saved to {output_path}")

    except Exception as e:
        logger.error(f"Error creating results visualization: {str(e)}")
        raise


def plot_distribution(data: pd.DataFrame, column: str, output_path: str):
    """
    绘制特定列的分布图
    
    Args:
        data: 包含要绘制的数据的DataFrame
        column: 要绘制的列名
        output_path: 输出文件路径
    """
    try:
        plt.figure(figsize=(10, 6))
        sns.histplot(data=data, x=column, kde=True)
        plt.title(f'Distribution of {column}')

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Distribution plot saved to {output_path}")

    except Exception as e:
        logger.error(f"Error creating distribution plot: {str(e)}")
        raise


def plot_correlation_matrix(data: pd.DataFrame, output_path: str):
    """
    绘制特征相关性矩阵
    
    Args:
        data: 包含特征的DataFrame
        output_path: 输出文件路径
    """
    try:
        plt.figure(figsize=(12, 10))
        correlation_matrix = data.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Feature Correlation Matrix')

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Correlation matrix plot saved to {output_path}")

    except Exception as e:
        logger.error(f"Error creating correlation matrix plot: {str(e)}")
        raise


def plot_attention_heatmap(attention_weights: np.ndarray, tokens: List[str], output_path: Path):
    """绘制注意力热力图"""
    try:
        plt.figure(figsize=(10, 8))

        sns.heatmap(
            attention_weights,
            xticklabels=tokens,
            yticklabels=tokens,
            cmap='viridis',
            center=0,
            square=True
        )

        plt.title('Attention Weights Heatmap')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Attention heatmap saved to {output_path}")

        plt.close()

    except Exception as e:
        logger.error(f"Error creating attention heatmap: {str(e)}")
        raise


def plot_theorem_complexity(theorems: List[Dict], output_path: Path):
    """绘制定理复杂度分析"""
    try:
        # 提取复杂度指标
        complexities = [t.get('complexity_score', 0) for t in theorems]
        domains = [t.get('domain', 'Unknown') for t in theorems]

        # 创建DataFrame
        df = pd.DataFrame({
            'Complexity': complexities,
            'Domain': domains
        })

        plt.figure(figsize=(12, 6))

        # 1. 复杂度分布箱线图
        sns.boxplot(x='Domain', y='Complexity', data=df)
        plt.title('Theorem Complexity Distribution by Domain')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Complexity analysis saved to {output_path}")

        plt.close()

    except Exception as e:
        logger.error(f"Error creating complexity analysis: {str(e)}")
        raise


def create_summary_report(results: Dict, output_path: Path):
    """创建结果总结报告"""
    try:
        report = {
            'verification_summary': {
                'total_theorems': len(results),
                'verification_rates': {
                    'symbolic': results['symbolic_validity_rate'],
                    'coq': results['coq_validity_rate'],
                    'lean': results['lean_validity_rate']
                }
            },
            'domain_distribution': results.get('domain_distribution', {}),
            'error_analysis': {
                'total_errors': sum(1 for r in results if 'error' in r),
                'error_types': {}
            }
        }

        # 保存报告
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Summary report saved to {output_path}")

    except Exception as e:
        logger.error(f"Error creating summary report: {str(e)}")
        raise


if __name__ == "__main__":
    # 测试可视化功能
    sample_results = [
        {
            'theorem': {'domain': 'algebra', 'statement': 'Sample theorem 1'},
            'symbolic_valid': True,
            'coq_valid': True,
            'lean_valid': False
        },
        {
            'theorem': {'domain': 'topology', 'statement': 'Sample theorem 2'},
            'symbolic_valid': True,
            'coq_valid': False,
            'lean_valid': True
        }
    ]

    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    # 测试各种可视化功能
    plot_results(sample_results, output_dir / 'verification_results.png')

    sample_history = {
        'train_loss': [0.5, 0.4, 0.3],
        'val_loss': [0.6, 0.5, 0.4],
        'train_acc': [0.8, 0.85, 0.9],
        'val_acc': [0.75, 0.8, 0.85]
    }

    plot_training_history(sample_history, output_dir / 'training_history.png')
