# src/models/train.py

import torch
from torch.utils.data import DataLoader
from transformers import AdamW


def train_model(model, train_dataloader, eval_dataloader, epochs=3):
    optimizer = AdamW(model.parameters())

    for epoch in range(epochs):
        model.train()
        for batch in train_dataloader:
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()

        # 评估
        model.eval()
        eval_loss = 0
        with torch.no_grad():
            for batch in eval_dataloader:
                outputs = model(**batch)
                eval_loss += outputs.loss.mean().item()

        print(f"Epoch {epoch}: eval_loss = {eval_loss/len(eval_dataloader)}")
