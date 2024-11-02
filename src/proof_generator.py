import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Dict
from tqdm import tqdm

logger = logging.getLogger(__name__)


class TheoremDataset(Dataset):
    def __init__(self, features, labels):
        self.features = torch.FloatTensor(features)
        self.labels = torch.FloatTensor(labels)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'labels': self.labels[idx]
        }


class ProofGenerator(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, output_dim: int = 1):
        super(ProofGenerator, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )

        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, output_dim)
        )

        self.criterion = nn.MSELoss()
        self.optimizer = None
        self.scheduler = None

    def forward(self, x):
        x = x.float()
        encoded = self.encoder(x)
        output = self.decoder(encoded)
        return output

    def configure_training(self,train_data: Tuple[np.ndarray, np.ndarray],val_data: Tuple[np.ndarray, np.ndarray],batch_size: int = 32,learning_rate: float = 1e-3,device="mps"):
        self.device = device
        self.to(self.device)
        train_features, train_labels = train_data
        val_features, val_labels = val_data

        train_features = train_features.astype(np.float32)
        train_labels = train_labels.astype(np.float32)
        val_features = val_features.astype(np.float32)
        val_labels = val_labels.astype(np.float32)

        self.train_dataset = TheoremDataset(train_features, train_labels)
        self.val_dataset = TheoremDataset(val_features, val_labels)

        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True
        )

        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=batch_size,
            shuffle=False
        )

        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.1,
            patience=5,
            verbose=True
        )

    def save_model(self, path: str):
        """保存模型状态"""
        save_dict = {
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'device': self.device
        }
        torch.save(save_dict, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str, device: str = None):
        """加载模型状态"""
        checkpoint = torch.load(path, map_location=device if device else self.device)
        
        if device:
            self.set_device(device)
            
        self.load_state_dict(checkpoint['model_state_dict'])
        
        if self.optimizer and checkpoint['optimizer_state_dict']:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if self.scheduler and checkpoint['scheduler_state_dict']:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
            
        if 'device' in checkpoint:
            self.device = checkpoint['device']
            
        logger.info(f"Model loaded from {path}")
    def set_device(self, device: str):
        """设置设备并移动模型"""
        self.device = torch.device(device)
        self.to(self.device)
        return self
    def train_model(self, num_epochs: int = 50, device: str = 'mps'):
        """训练模型"""
        if self.optimizer is None:
            raise ValueError("Must call configure_training before training!")

        logger.info(f"Training on device: {self.device}")
        self.to(self.device)

        best_val_loss = float('inf')
        history = {
            'train_loss': [],
            'val_loss': []
        }

        for epoch in range(num_epochs):
            # 训练阶段
            self.train()
            train_losses = []

            pbar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")
            for batch in pbar:
                features = batch['features'].float().to(device)
                labels = batch['labels'].float().to(device)

                self.optimizer.zero_grad()
                outputs = self(features)
                loss = self.criterion(outputs, labels)

                loss.backward()
                self.optimizer.step()

                train_losses.append(loss.item())
                pbar.set_postfix({'loss': loss.item()})

            avg_train_loss = np.mean(train_losses)
            history['train_loss'].append(avg_train_loss)

            # 验证阶段
            self.eval()
            val_losses = []

            with torch.no_grad():
                for batch in self.val_loader:
                    features = batch['features'].float().to(device)
                    labels = batch['labels'].float().to(device)

                    outputs = self(features)
                    loss = self.criterion(outputs, labels)
                    val_losses.append(loss.item())

            avg_val_loss = np.mean(val_losses)
            history['val_loss'].append(avg_val_loss)

            # 更新学习率
            self.scheduler.step(avg_val_loss)

            # 保存最佳模型
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                self.save_model('best_model.pt')

            logger.info(
                f"Epoch {epoch+1}: train_loss={avg_train_loss:.4f}, val_loss={avg_val_loss:.4f}")

        return history

    def generate_proofs(self, features: np.ndarray) -> list[str]:
        """为一组定理生成证明"""
        self.eval()
        device = next(self.parameters()).device
        features_tensor = torch.FloatTensor(features).to(device)

        with torch.no_grad():
            outputs = self(features_tensor)

        # 这里简单返回一些示例证明
        proofs = [f"Proof {i+1}: Using the model output {output.item():.4f}"
                  for i, output in enumerate(outputs)]
        return proofs


def create_proof_generator(train_data: Tuple[np.ndarray, np.ndarray],
                           val_data: Tuple[np.ndarray, np.ndarray],
                           device: str = 'mps') -> ProofGenerator:
    input_dim = train_data[0].shape[1]
    model = ProofGenerator(input_dim=input_dim).to(device)
    model.configure_training(
        train_data=train_data,
        val_data=val_data
    )
    return model
