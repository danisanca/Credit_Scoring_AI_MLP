"""
test_model.py
Testes unitarios do modelo de rede neural CreditScoringMLP.
Escrito para rodar sem GPU e sem pesos salvos — testa a logica pura.
"""

import pytest
import torch
from src.model import CreditScoringMLP


@pytest.fixture
def modelo():
    """Fixture que instancia o modelo com parametros default."""
    return CreditScoringMLP(input_size=7, dropout_rate=0.3)


@pytest.fixture
def batch_trivial():
    """Fixture com um batch de 4 amostras, 7 features cada."""
    return torch.randn(4, 7)


def test_instancia_modelo(modelo):
    """Garante que o modelo instancia corretamente e e um nn.Module."""
    assert isinstance(modelo, CreditScoringMLP)
    assert modelo.training is True


def test_forward_retorna_tensor(modelo, batch_trivial):
    """Forward pass retorna tensor com shape correto."""
    output = modelo(batch_trivial)
    assert isinstance(output, torch.Tensor)
    assert output.shape == (4, 1)


def test_output_probabilidade(modelo, batch_trivial):
    """A saida deve estar entre 0 e 1 (Sigmoid)."""
    output = modelo(batch_trivial)
    assert torch.all(output >= 0)
    assert torch.all(output <= 1)


def test_parametros_aprendiveis(modelo):
    """O modelo deve ter parametros treinaveis."""
    params = list(modelo.parameters())
    assert len(params) > 0
    total = sum(p.numel() for p in params)
    assert total > 0


def test_batch_tamanhos_variados(modelo):
    """O modelo deve aceitar batches de diferentes tamanhos."""
    for batch_size in [1, 8, 32, 64]:
        x = torch.randn(batch_size, 7)
        y = modelo(x)
        assert y.shape == (batch_size, 1)


def test_dropout_diferente_do_zero():
    """Dropout deve alterar os outputs entre runs em modo training."""
    torch.manual_seed(42)
    modelo = CreditScoringMLP(dropout_rate=0.5)
    x = torch.randn(10, 7)
    y1 = modelo(x)
    y2 = modelo(x)
    # Com dropout alto, as saidas devem ser diferentes
    assert not torch.allclose(y1, y2, atol=1e-5)


def test_inferencia_eval():
    """Em modo eval, o dropout e desligado e saidas devem ser deterministicas."""
    torch.manual_seed(42)
    modelo = CreditScoringMLP()
    x = torch.randn(10, 7)
    modelo.eval()
    with torch.no_grad():
        y1 = modelo(x)
        y2 = modelo(x)
    assert torch.allclose(y1, y2)


def test_gradientes_fluxo_backward(modelo, batch_trivial):
    """Backward pass deve computar gradientes nos parametros."""
    output = modelo(batch_trivial)
    loss = output.sum()
    loss.backward()
    for param in modelo.parameters():
        assert param.grad is not None
        assert not torch.all(param.grad == 0)


def test_arquitetura_camadas(modelo):
    """Verifica se a arquitetura tem a estrutura esperada (7->64->32->16->1)."""
    camadas = [m for m in modelo.modules() if isinstance(m, torch.nn.Linear)]
    assert len(camadas) == 4
    assert camadas[0].in_features == 7
    assert camadas[0].out_features == 64
    assert camadas[3].out_features == 1
