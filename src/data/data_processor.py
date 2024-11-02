# src/data/data_processor.py

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, data_dir="data", random_state=42):
        self.data_dir = Path(data_dir)
        self.random_state = random_state
        self.domains = ["algebra", "topology", "number_theory"]

    def generate_sample_data(self):
        """生成示例数据"""
        logger.info("Generating sample data...")

        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 每个领域的定理模板
        templates = {
            "algebra": [
                "For all elements x in Ring R, if x^2 = 0 then x = 0",
                "The sum of squares formula: (a + b)^2 = a^2 + 2ab + b^2",
                "For matrices A and B, (AB)^T = B^T A^T"
            ],
            "topology": [
                "Every compact subset of a Hausdorff space is closed",
                "The continuous image of a compact set is compact",
                "A continuous bijection from a compact space to a Hausdorff space is a homeomorphism"
            ],
            "number_theory": [
                "For any prime p, if p divides ab then p divides a or p divides b",
                "There are infinitely many prime numbers",
                "Every positive integer greater than 1 has a prime factorization"
            ]
        }

        # 为每个领域生成数据
        for domain in self.domains:
            domain_dir = self.data_dir / domain
            domain_dir.mkdir(exist_ok=True)

            theorems = []
            for i in range(100):  # 每个领域生成100个定理
                theorem = {
                    "id": f"{domain}_{i}",
                    "statement": np.random.choice(templates[domain]),
                    "domain": domain,
                    "difficulty": np.random.choice(["easy", "medium", "hard"]),
                    "complexity_score": np.random.uniform(0, 1),
                    "proof": f"This is a sample proof for theorem {i} in {domain}.",
                    "symbols": ["∀", "∃", "∈", "⊆", "∪", "∩"],
                    "prerequisites": []
                }
                theorems.append(theorem)

            # 保存到JSON文件
            with open(domain_dir / "theorems.json", "w") as f:
                json.dump({"theorems": theorems}, f, indent=2)

            logger.info(f"Generated {len(theorems)} theorems for {domain}")

    def load_raw_data(self) -> Dict[str, List[Dict]]:
        """加载原始数据，如果不存在则生成示例数据"""
        raw_data = {}

        # 检查数据文件是否存在
        all_files_exist = True
        for domain in self.domains:
            domain_path = self.data_dir / domain / "theorems.json"
            if not domain_path.exists():
                all_files_exist = False
                break

        # 如果数据文件不存在，生成示例数据
        if not all_files_exist:
            logger.info("Data files not found. Generating sample data...")
            self.generate_sample_data()

        # 加载数据
        for domain in self.domains:
            domain_path = self.data_dir / domain / "theorems.json"
            with open(domain_path) as f:
                data = json.load(f)
                raw_data[domain] = data["theorems"]

        return raw_data

    def preprocess_theorem(self, theorem: Dict) -> Dict:
        """预处理单个定理"""
        processed = {
            "id": theorem["id"],
            "statement": theorem["statement"],
            "domain": theorem["domain"],
            "difficulty": theorem["difficulty"],
            "complexity_score": theorem.get("complexity_score", 0.5),
            "proof_length": len(theorem.get("proof", "").split()),
            "num_symbols": len(theorem.get("symbols", [])),
            "num_prerequisites": len(theorem.get("prerequisites", []))
        }
        return processed

    def prepare_datasets(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """准备训练、验证和测试数据集"""
        # 加载原始数据
        raw_data = self.load_raw_data()

        # 处理所有定理
        processed_theorems = []
        for domain, theorems in raw_data.items():
            for theorem in theorems:
                processed_theorem = self.preprocess_theorem(theorem)
                processed_theorems.append(processed_theorem)

        # 转换为DataFrame
        df = pd.DataFrame(processed_theorems)

        # 分割数据集
        train_df, temp_df = train_test_split(
            df, test_size=0.3, random_state=self.random_state
        )
        val_df, test_df = train_test_split(
            temp_df, test_size=0.5, random_state=self.random_state
        )

        logger.info(f"Dataset split: train{len(train_df)}, val={len(val_df)}, test={len(test_df)}")

        return train_df, val_df, test_df

    def save_datasets(self, train_df: pd.DataFrame, val_df: pd.DataFrame,
                      test_df: pd.DataFrame, output_dir: str = "processed_data"):
        """保存处理后的数据集"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        train_df.to_csv(output_path / "train.csv", index=False)
        val_df.to_csv(output_path / "val.csv", index=False)
        test_df.to_csv(output_path / "test.csv", index=False)

        logger.info(f"Saved processed datasets to {output_dir}")


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试数据处理
    processor = DataProcessor()
    train_df, val_df, test_df = processor.prepare_datasets()
    processor.save_datasets(train_df, val_df, test_df)
