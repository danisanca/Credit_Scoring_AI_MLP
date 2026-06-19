"""
dataset.py
Carregamento, pré-processamento e normalização dos dados de crédito.
Usa StandardScaler para normalização e salva o scaler para uso em produção.
"""

import os
import joblib
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "idade",
    "renda_mensal",
    "tempo_emprego_meses",
    "divida_total",
    "qtd_emprestimos",
    "historico_pagamento",
    "valor_solicitado",
]
TARGET_COLUMN = "inadimplente"
SCALER_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "scaler.joblib")


class CreditDataset(Dataset):
    """Dataset PyTorch para dados de crédito pré-processados."""

    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int):
        return self.X[idx], self.y[idx]


def load_and_split(csv_path: str, test_size: float = 0.2, val_size: float = 0.1):
    """
    Carrega o CSV, normaliza e retorna (train, val, test) DataLoaders.
    Salva o scaler para reutilização na API de produção.
    """
    df = pd.read_csv(csv_path)

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    # Separa treino/validação/teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=val_size / (1 - test_size), random_state=42, stratify=y_train
    )

    # Normaliza com StandardScaler (fit apenas no treino para evitar data leakage)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    # Salva o scaler para uso na API
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)

    print(f"✅ Scaler salvo em: {SCALER_PATH}")
    print(f"   Treino: {len(X_train)} | Validação: {len(X_val)} | Teste: {len(X_test)}")

    return (
        CreditDataset(X_train, y_train),
        CreditDataset(X_val, y_val),
        CreditDataset(X_test, y_test),
        y_train,
    )


def load_scaler() -> StandardScaler:
    """Carrega o scaler salvo durante o treinamento."""
    return joblib.load(SCALER_PATH)
