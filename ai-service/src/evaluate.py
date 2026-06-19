"""
evaluate.py
Geração de métricas completas: Classification Report, Matriz de Confusão e ROC-AUC.
"""

import os
import torch
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    f1_score,
)


def evaluate_model(model, data_loader, device):
    """Avalia o modelo e imprime métricas profissionais."""
    model.eval()
    all_probs, all_preds, all_labels = [], [], []

    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch)
            probs = torch.sigmoid(outputs).cpu().numpy()
            preds = (probs > 0.5).astype(int)
            all_probs.extend(probs.flatten())
            all_preds.extend(preds.flatten())
            all_labels.extend(y_batch.numpy().flatten())

    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)

    roc_auc = roc_auc_score(all_labels, all_probs)
    f1 = f1_score(all_labels, all_preds)
    cm = confusion_matrix(all_labels, all_preds)

    print("\n" + "=" * 55)
    print("📊  RELATÓRIO DE AVALIAÇÃO — Credit Scoring MLP")
    print("=" * 55)
    print(classification_report(all_labels, all_preds, target_names=["Adimplente", "Inadimplente"]))
    print(f"ROC-AUC Score : {roc_auc:.4f}")
    print(f"F1-Score      : {f1:.4f}")
    print(f"\nMatriz de Confusão:")
    print(f"  TN={cm[0,0]:>5}  FP={cm[0,1]:>5}")
    print(f"  FN={cm[1,0]:>5}  TP={cm[1,1]:>5}")
    print("=" * 55)

    return {
        "roc_auc": float(roc_auc),
        "f1_score": float(f1),
        "confusion_matrix": cm.tolist(),
    }
