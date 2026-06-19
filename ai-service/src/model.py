"""
model.py
Arquitetura da Rede Neural MLP (Multi-Layer Perceptron) para Credit Scoring.
Usa PyTorch com Dropout para regularização e evitar overfitting.
"""

import torch
import torch.nn as nn


class CreditScoringMLP(nn.Module):
    """
    Rede Neural de 3 camadas ocultas para previsão de risco de crédito.
    Arquitetura: Input(7) -> 64 -> 32 -> 16 -> Output(1)
    """

    def __init__(self, input_size: int = 7, dropout_rate: float = 0.3):
        super(CreditScoringMLP, self).__init__()

        self.network = nn.Sequential(
            # Camada de entrada -> primeira oculta
            nn.Linear(input_size, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),

            # Segunda camada oculta
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(dropout_rate),

            # Terceira camada oculta
            nn.Linear(32, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Dropout(dropout_rate / 2),

            # Camada de saída (probabilidade de inadimplência)
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)
