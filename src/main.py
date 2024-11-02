import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import logging
import argparse
from pathlib import Path
import numpy as np
import torch
from data.data_processor import DataProcessor
from data.feature_engineering import FeatureEngineer 
from proof_generator import ProofGenerator, create_proof_generator
from proof_verifier import ProofVerifier
from theorem_generator import TheoremGenerator
from visualization import plot_results, plot_training_history

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_args():
    parser = argparse.ArgumentParser(
        description='ProofMind: Mathematical Theorem Proof Generation')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory containing the theorem data')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save results')
    parser.add_argument('--mode', type=str, choices=['train', 'eval', 'all'],
                        default='all', help='Run mode')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                        help='Learning rate')
    return parser.parse_args()


# src/main.py 的 process_data 函数

def process_data(args):
    """数据处理流程"""
    logger.info("Starting data processing...")

    # 初始化数据处理器和特征工程器
    processor = DataProcessor(data_dir=args.data_dir)
    feature_engineer = FeatureEngineer()

    # 加载和分割数据
    train_df, val_df, test_df = processor.prepare_datasets()

    # 准备特征
    train_features, val_features, test_features = feature_engineer.prepare_features(
        train_df, val_df, test_df
    )

    # 准备标签（使用复杂度分数作为目标）
    train_labels = train_df['complexity_score'].values.reshape(
        -1, 1).astype(np.float32)
    val_labels = val_df['complexity_score'].values.reshape(
        -1, 1).astype(np.float32)
    test_labels = test_df['complexity_score'].values.reshape(
        -1, 1).astype(np.float32)

    return {
        'train': (train_df, train_features, train_labels),
        'val': (val_df, val_features, val_labels),
        'test': (test_df, test_features, test_labels),
        'feature_dim': train_features.shape[1]
    }


def train(args, data):
    """训练流程"""
    logger.info("Starting training...")

    # 准备数据
    train_df, train_features, train_labels = data['train']
    val_df, val_features, val_labels = data['val']
    feature_dim = data['feature_dim']

    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # 确保数据类型为float32
    train_features = train_features.astype(np.float32)
    train_labels = train_labels.astype(np.float32)
    val_features = val_features.astype(np.float32)
    val_labels = val_labels.astype(np.float32)

    # 创建模型
    model = create_proof_generator(
        train_data=(train_features, train_labels),
        val_data=(val_features, val_labels),
        device=device
    )

    # 训练模型
    history = model.train_model(num_epochs=args.epochs, device=device)

    # 保存训练历史
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_training_history(history, output_dir / 'training_history.png')

    logger.info("Training completed successfully")
    return model
# main.py 中的 evaluate 函数修改


def evaluate(args, model, data):
    """评估流程"""
    logger.info("Starting evaluation...")

    # 正确解包测试数据
    test_df, test_features, test_labels = data['test']

    # 生成证明
    try:
        proofs = model.generate_proofs(test_features)

        # 准备验证结果
        results = []
        for i, proof in enumerate(proofs):
            # 直接使用模型的 forward 方法，它会处理设备转换
            pred_tensor = model(torch.FloatTensor(test_features[i:i+1]))
            pred_score = float(pred_tensor.detach().cpu().numpy())

            result = {
                'theorem_id': test_df.iloc[i]['id'] if 'id' in test_df.columns else f'theorem_{i}',
                'domain': test_df.iloc[i]['domain'] if 'domain' in test_df.columns else 'unknown',
                'predicted_score': pred_score,
                'actual_score': float(test_labels[i]),
                'proof': proof
            }
            results.append(result)

        # 进行验证
        verifier = ProofVerifier()
        verification_results = verifier.verify_proofs(results)

        # 保存结果
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 可视化结果
        plot_results(verification_results, output_dir /
                     'verification_results.png')

        logger.info("Evaluation completed successfully")
        return verification_results

    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise


def calculate_metrics(results):
    """计算评估指标"""
    predictions = np.array([r['predicted_score'] for r in results])
    targets = np.array([r['actual_score'] for r in results])

    mse = np.mean((predictions - targets) ** 2)
    mae = np.mean(np.abs(predictions - targets))

    return {
        'mse': float(mse),
        'mae': float(mae),
        'num_theorems': len(results)
    }


def save_results(results, output_path):
    """保存评估结果到文件"""
    with open(output_path, 'w') as f:
        json.dump({
            'results': results,
            'timestamp': datetime.datetime.now().isoformat()
        }, f, indent=2)


def main():
    args = setup_args()

    try:
        # 数据处理
        data = process_data(args)

        # 训练
        if args.mode in ['train', 'all']:
            model = train(args, data)
            model.save_model(Path(args.output_dir) / 'final_model.pt')

        # 评估
        if args.mode in ['eval', 'all']:
            if 'model' not in locals():
                # 如果没有刚训练的模型，加载保存的模型
                model = ProofGenerator(input_dim=data['feature_dim'])
                model.load_model(Path(args.output_dir) / 'final_model.pt')

            results = evaluate(args, model, data)
            logger.info("Results saved to output directory")

        logger.info("Pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()
