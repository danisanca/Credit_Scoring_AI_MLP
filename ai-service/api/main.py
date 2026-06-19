"""
api/main.py
FastAPI — Serviço de predição de risco de crédito.
Endpoints: GET /health | POST /predict
"""

import os
import sys
import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.model import CreditScoringMLP
from src.dataset import load_scaler

# ──────────────────────────────────────────────
# Configuração do App
# ──────────────────────────────────────────────
app = FastAPI(
    title="Credit Scoring AI — API",
    description="Serviço de predição de risco de crédito com Rede Neural MLP (PyTorch).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = torch.device("cpu")  # Em produção sem GPU usamos CPU
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "credit_model.pth")

# ──────────────────────────────────────────────
# Carrega modelo e scaler na inicialização
# ──────────────────────────────────────────────
model = CreditScoringMLP(input_size=7)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

scaler = load_scaler()

print("✅ Modelo e Scaler carregados com sucesso.")


# ──────────────────────────────────────────────
# Schemas de Request/Response (Pydantic)
# ──────────────────────────────────────────────
class PredictRequest(BaseModel):
    idade: int = Field(..., ge=18, le=100, example=35)
    renda_mensal: float = Field(..., gt=0, example=5000.0)
    tempo_emprego_meses: int = Field(..., ge=0, example=36)
    divida_total: float = Field(..., ge=0, example=15000.0)
    qtd_emprestimos: int = Field(..., ge=0, example=2)
    historico_pagamento: int = Field(..., ge=0, le=100, example=75)
    valor_solicitado: float = Field(..., gt=0, example=20000.0)


class PredictResponse(BaseModel):
    score: float
    classificacao: str
    probabilidade_inadimplencia: float
    aprovado: bool


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "model": "credit_mlp_v1", "device": str(DEVICE)}


@app.post("/predict", response_model=PredictResponse, tags=["Predição"])
def predict(data: PredictRequest):
    try:
        features = np.array([[
            data.idade,
            data.renda_mensal,
            data.tempo_emprego_meses,
            data.divida_total,
            data.qtd_emprestimos,
            data.historico_pagamento,
            data.valor_solicitado,
        ]], dtype=np.float32)

        # Normaliza com o scaler do treinamento
        features_scaled = scaler.transform(features)
        tensor = torch.tensor(features_scaled, dtype=torch.float32)

        with torch.no_grad():
            prob = model(tensor).item()

        # Classifica o risco
        if prob < 0.3:
            classificacao = "Baixo"
        elif prob < 0.6:
            classificacao = "Médio"
        else:
            classificacao = "Alto"

        aprovado = prob < 0.5

        return PredictResponse(
            score=round(1.0 - prob, 4),       # Score positivo: quanto maior, melhor o pagador
            classificacao=classificacao,
            probabilidade_inadimplencia=round(prob, 4),
            aprovado=aprovado,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")
