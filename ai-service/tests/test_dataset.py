"""
test_dataset.py
Testes do carregamento e pre-processamento de dados.
Esses testes funcionam com o dataset sintetico gerado pelo generate_data.py.
"""

import os
import pytest
import pandas as pd
import numpy as np
import torch
from src.dataset import load_and_split, FEATURE_COLUMNS, TARGET_COLUMN


# Fixture compartilhada — sobe o CSV sintetico se nao existir
@pytest.fixture(scope="module")
def csv_path():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "credit_dataset.csv")
    if not os.path.exists(path):
        pytest.skip("Dataset credit_dataset.csv nao encontrado. Execute generate_data.py primeiro.")
    return path


@pytest.fixture
def loaders(csv_path):
    """Retorna os tres DataLoaders carregados a partir do CSV."""
    return load_and_split(csv_path, test_size=0.2, val_size=0.1)


def test_csv_existe(csv_path):
    assert os.path.isfile(csv_path)


def test_colunas_necessarias(csv_path):
    df = pd.read_csv(csv_path)
    for col in FEATURE_COLUMNS:
        assert col in df.columns
    assert TARGET_COLUMN in df.columns


def test_target_binario(csv_path):
    """A coluna target deve conter apenas 0 e 1."""
    df = pd.read_csv(csv_path)
    assert set(df[TARGET_COLUMN].unique()).issubset({0, 1})


def test_sem_valores_nulos(csv_path):
    """O dataset nao deve ter valores faltantes."""
    df = pd.read_csv(csv_path)
    assert not df.isnull().any().any()


def test_carregamento_shapes(loaders):
    """Verifica se os DataLoaders retornam tensores com shapes corretos."""
    train_loader, val_loader, test_loader = loaders

    X_train, y_train = next(iter(train_loader))
    assert X_train.shape[1] == len(FEATURE_COLUMNS)
    assert y_train.shape == (len(X_train), 1)
    assert X_train.dtype == torch.float32


def test_scaler_salvo(loaders):
    """O StandardScaler deve ser salvo em disco apos load_and_split."""
    from src.dataset import SCALER_PATH
    assert os.path.isfile(SCALER_PATH), f"Scaler nao encontrado em {SCALER_PATH}"


def test_normalizacao_media_zero(loaders):
    """Apos StandardScaler, a media do training set deve ser proxima de 0."""
    train_loader, _, _ = loaders
    all_X = []
    for X, _ in train_loader:
        all_X.append(X.numpy())
    all_X = np.concatenate(all_X, axis=0)
    mean = np.mean(all_X, axis=0)
    assert np.allclose(mean, 0, atol=0.15)


def test_dataset_balanceamento(csv_path):
    """Verifica se o dataset tem as duas classes presentes."""
    df = pd.read_csv(csv_path)
    counts = df[TARGET_COLUMN].value_counts()
    assert 0 in counts.index
    assert 1 in counts.index


def test_proporcao_treino_validacao_teste(csv_path):
    """As proporcoes de split devem ser razoaveis."""
    train_loader, val_loader, test_loader = load_and_split(csv_path, test_size=0.2, val_size=0.1)
    n_train = len(train_loader.dataset)
    n_val = len(val_loader.dataset)
    n_test = len(test_loader.dataset)
    total = n_train + n_val + n_test
    assert abs(n_train / total - 0.70) < 0.05
    assert abs(n_val / total - 0.10) < 0.02
    assert abs(n_test / total - 0.20) < 0.02


def test_feature_ranges(csv_path):
    """Features numericas nao devem conter valores absurdos."""
    df = pd.read_csv(csv_path)
    assert df["idade"].between(18, 70).all()
    assert df["renda_mensal"].between(900, 30000).all()
    assert df["qtd_emprestimos"].between(0, 10).all()
