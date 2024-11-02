# src/data/validate_data.py

import json
import numpy as np
import pandas as pd
from pathlib import Path


def validate_processed_data():
    """验证处理后的数据的完整性和正确性"""
    processed_dir = Path("processed_data")

    # 检查必要文件是否存在
    required_files = [
        "train.csv", "val.csv", "test.csv",
        "train_features.npy", "val_features.npy", "test_features.npy"
    ]

    for file in required_files:
        if not (processed_dir / file).exists():
            print(f"Warning: {file} not found!")
            continue

        # 验证数据
        if file.endswith('.csv'):
            df = pd.read_csv(processed_dir / file)
            print(f"\nValidating {file}:")
            print(f"Number of samples: {len(df)}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Missing values: {df.isnull().sum().sum()}")

        elif file.endswith('.npy'):
            features = np.load(processed_dir / file)
            print(f"\nValidating {file}:")
            print(f"Shape: {features.shape}")
            print(f"Data type: {features.dtype}")
            print(f"Contains NaN: {np.isnan(features).any()}")


if __name__ == "__main__":
    validate_processed_data()
