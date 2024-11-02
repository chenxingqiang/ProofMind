# src/data/feature_engineering.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.numerical_features = [
            'complexity_score',
            'proof_length',
            'num_symbols',
            'num_prerequisites'
        ]

        self.categorical_features = [
            'difficulty',
            'domain'
        ]

    def _encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """对分类特征进行编码"""
        # 对difficulty进行编码
        difficulty_map = {
            'easy': 0,
            'medium': 1,
            'hard': 2
        }
        df['difficulty_encoded'] = df['difficulty'].map(difficulty_map)

        # 对domain进行one-hot编码
        domain_dummies = pd.get_dummies(df['domain'], prefix='domain')
        df = pd.concat([df, domain_dummies], axis=1)

        return df

    def _create_numerical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建数值特征"""
        # 确保所有数值特征都存在
        for feature in self.numerical_features:
            if feature not in df.columns:
                df[feature] = 0  # 设置默认值

        # 标准化数值特征
        df[self.numerical_features] = self.scaler.fit_transform(
            df[self.numerical_features])

        return df

    def prepare_features(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame
                         ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """准备特征数据"""
        logger.info("Preparing features...")

        # 处理训练集
        train_features = self._create_features(train_df)

        # 处理验证集和测试集（使用与训练集相同的转换）
        val_features = self._transform_features(val_df)
        test_features = self._transform_features(test_df)

        logger.info(f"Feature shapes - train: {train_features.shape}, val: {val_features.shape}, test: {test_features.shape}")

        return train_features, val_features, test_features

    def _create_features(self, df: pd.DataFrame) -> np.ndarray:
        """创建特征矩阵"""
        # 编码分类特征
        df = self._encode_categorical_features(df)

        # 创建数值特征
        df = self._create_numerical_features(df)

        # 选择最终特征
        feature_columns = (
            self.numerical_features +
            ['difficulty_encoded'] +
            [col for col in df.columns if col.startswith('domain_')]
        )

        return df[feature_columns].values.astype(np.float32)

    def _transform_features(self, df: pd.DataFrame) -> np.ndarray:
        """使用已经拟合的转换器转换特征"""
        df = self._encode_categorical_features(df)
        df[self.numerical_features] = self.scaler.transform(
            df[self.numerical_features])

        feature_columns = (
            self.numerical_features +
            ['difficulty_encoded'] +
            [col for col in df.columns if col.startswith('domain_')]
        )

        return df[feature_columns].values.astype(np.float32)


def get_feature_names(df: pd.DataFrame) -> List[str]:
    """获取特征名称列表"""
    numerical_features = [
        'complexity_score',
        'proof_length',
        'num_symbols',
        'num_prerequisites'
    ]

    categorical_features = ['difficulty_encoded']
    domain_features = [col for col in df.columns if col.startswith('domain_')]

    return numerical_features + categorical_features + domain_features
