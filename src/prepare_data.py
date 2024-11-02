# src/prepare_data.py

import pandas as pd
import numpy as np
from src.data.feature_engineering import FeatureEngineer
from src.data.data_processor import DataProcessor
from src.data.data_downloader import DataDownloader
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


def main():
    print("Starting data preparation...")

    # 1. 生成示例数据
    print("\nStep 1: Generating sample data")
    downloader = DataDownloader()
    downloader.create_sample_data()

    # 2. 处理数据
    print("\nStep 2: Processing data")
    processor = DataProcessor()
    train_df, val_df, test_df = processor.prepare_datasets()
    processor.save_datasets(train_df, val_df, test_df)

    # 3. 特征工程
    print("\nStep 3: Engineering features")
    engineer = FeatureEngineer()

    # 确保所有必需的列都存在
    required_columns = ['statement', 'complexity_score', 'proof_length']
    for df in [train_df, val_df, test_df]:
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0  # 为缺失列添加默认值

    train_features, feature_names = engineer.create_features(train_df)
    val_features = engineer.transform_features(val_df)
    test_features = engineer.transform_features(test_df)

    # 4. 保存处理后的数据
    print("\nStep 4: Saving processed data")
    output_dir = Path("processed_data")
    output_dir.mkdir(exist_ok=True)

    np.save(output_dir / "train_features.npy", train_features)
    np.save(output_dir / "val_features.npy", val_features)
    np.save(output_dir / "test_features.npy", test_features)

    # 5. 打印数据集信息
    print("\nData preparation completed!")
    print(f"Training samples: {len(train_df)}")
    print(f"Validation samples: {len(val_df)}")
    print(f"Test samples: {len(test_df)}")
    if len(train_features) > 0:
        print(f"Feature dimension: {train_features.shape[1]}")

    # 6. 保存一些示例数据供查看
    print("\nSaving sample data for inspection...")
    sample_data = {
        'train': train_df.head().to_dict('records'),
        'val': val_df.head().to_dict('records'),
        'test': test_df.head().to_dict('records')
    }

    with open(output_dir / "sample_data.json", 'w') as f:
        json.dump(sample_data, f, indent=2)

    print("\nSample data saved to processed_data/sample_data.json")


if __name__ == "__main__":
    main()
