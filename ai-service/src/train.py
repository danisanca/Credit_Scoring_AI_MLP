"""
train.py
Loop de treinamento da Rede Neural MLP para Credit Scoring.
Implementa: early stopping, class weighting para dados desbalanceados,
e salva o melhor modelo por F1-Score de validação.
"""

import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import f1_score
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.model import CreditScoringMLP
from src.dataset import load_and_split

# Configurações
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "credit_data.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "credit_model.pth")
EPOCHS = 60
BATCH_SIZE = 256
LEARNING_RATE = 1e-3
PATIENCE = 10  # Early stopping
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def compute_class_weights(y_train: np.ndarray) -> torch.Tensor:
    """Calcula pesos de classe para lidar com desbalanceamento."""
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    weight = torch.tensor([n_neg / n_pos], dtype=torch.float32).to(DEVICE)
    return weight


def train():
    print(f"🚀 Iniciando treinamento no dispositivo: {DEVICE}")

    # Carrega dados
    train_ds, val_ds, test_ds, y_train = load_and_split(DATA_PATH)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

    # Modelo, loss e otimizador
    model = CreditScoringMLP(input_size=7).to(DEVICE)
    pos_weight = compute_class_weights(y_train)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    best_f1 = 0.0
    patience_counter = 0

    print(f"\n{'Epoch':>6} | {'Train Loss':>10} | {'Val Loss':>10} | {'Val F1':>8} | {'Best':>6}")
    print("-" * 55)

    for epoch in range(1, EPOCHS + 1):
        # --- Treino ---
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)

        # --- Validação ---
        model.eval()
        val_loss = 0.0
        all_preds, all_labels = [], []
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
                outputs = model(X_batch)
                val_loss += criterion(outputs, y_batch).item()
                preds = (torch.sigmoid(outputs) > 0.5).float()
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(y_batch.cpu().numpy())

        val_loss /= len(val_loader)
        val_f1 = f1_score(all_labels, all_preds, zero_division=0)
        scheduler.step(val_loss)

        is_best = val_f1 > best_f1
        if is_best:
            best_f1 = val_f1
            patience_counter = 0
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            torch.save(model.state_dict(), MODEL_PATH)
        else:
            patience_counter += 1

        if epoch % 5 == 0 or is_best:
            marker = "✅" if is_best else "  "
            print(f"{epoch:>6} | {train_loss:>10.4f} | {val_loss:>10.4f} | {val_f1:>8.4f} | {marker}")

        if patience_counter >= PATIENCE:
            print(f"\n⏹️  Early stopping na época {epoch}. Melhor F1: {best_f1:.4f}")
            break

    # --- Avaliação final no conjunto de teste ---
    print(f"\n📊 Avaliando no conjunto de teste...")
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    from src.evaluate import evaluate_model
    evaluate_model(model, test_loader, DEVICE)

    print(f"\n✅ Modelo salvo em: {MODEL_PATH}")


if __name__ == "__main__":
    train()
