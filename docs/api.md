# Documentacao de API — Credit Scoring AI

## Backend .NET (Porta 5000)

### Endpoints Disponiveis

#### GET /swagger

Interface grafica interativa com todos os endpoints. Acesse em: `http://localhost:5000/swagger`

---

#### GET /api/creditanalises

Retorna todas as analises de credito realizadas.

**Resposta:**
```json
[
  {
    "id": 1,
    "cliente": "Joao Silva",
    "score": 0.15,
    "limiar": 0.50,
    "decisao": "APROVADO",
    "dataAnalise": "2026-06-15T10:30:00"
  }
]
```

---

#### POST /api/creditanalises

Solicita uma nova analise de credito. O backend delega para o AI Service.

**Corpo da Requisicao:**
```json
{
  "cliente": "Maria Oliveira",
  "idade": 35,
  "rendaMensal": 4500.00,
  "tempoEmpregoMeses": 24,
  "dividaTotal": 12000.00,
  "qtdEmprestimos": 2,
  "historicoPagamento": 1,
  "valorSolicitado": 5000.00
}
```

**Resposta:**
```json
{
  "id": 42,
  "cliente": "Maria Oliveira",
  "score": 0.72,
  "limiar": 0.50,
  "decisao": "REPROVADO",
  "dataAnalise": "2026-06-15T10:30:00"
}
```

**Codigos de Status:**
| Codigo | Significado |
|--------|-------------|
| 201 | Analise criada com sucesso |
| 400 | Dados invalidos (idade negativa, renda negativa) |
| 503 | AI Service indisponivel |

---

#### GET /api/creditanalises/{id}

Retorna uma analise especifica pelo ID.

---

## AI Service FastAPI (Porta 8000)

### Endpoints Disponiveis

#### GET /docs

Documentacao interativa (Swagger UI) do FastAPI.

---

#### GET /health

Healthcheck do servico e do modelo carregado.

**Resposta:**
```json
{
  "status": "UP",
  "model_loaded": true,
  "model_version": "1.0.0"
}
```

---

#### GET /predict

Executa a inferencia no modelo MLP para um cliente.

**Parametros de Query:**
| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| idade | int | Sim | Idade do cliente (18-70) |
| renda_mensal | float | Sim | Renda em R$ |
| tempo_emprego_meses | int | Sim | Meses no emprego atual |
| divida_total | float | Sim | Divida total em R$ |
| qtd_emprestimos | int | Sim | Numero de emprestimos ativos |
| historico_pagamento | int | Sim | Score historico (0-2) |
| valor_solicitado | float | Sim | Valor solicitado |

**Resposta:**
```json
{
  "probabilidade": 0.72,
  "limiar": 0.50,
  "decisao": "REPROVADO",
  "risco": "ALTO"
}
```

**Fluxo Interno:**
```
1. Recebe dados via query params
2. Normaliza com StandardScaler (scaler.joblib)
3. Forward pass no CreditScoringMLP (modelo.pth)
4. Sigmoid para probabilidade
5. Compara com threshold (0.5) para decisao
6. Classifica risco: <0.3 BAIXO, 0.3-0.7 MEDIO, >0.7 ALTO
```

## Contratos de Erro

Ambos os servicos retornam erros no formato:

```json
{
  "detail": "Descricao do erro",
  "error_code": "VALIDATION_ERROR"
}
```

## Autenticacao

Atualmente os endpoints sao publicos. No roadmap esta a adicao de autenticacao JWT via ASP.NET Identity.

## Variaveis de Ambiente

| Variavel | Default | Descricao |
|----------|---------|-----------|
| `CONNECTION_STRING` | localhost:5432 | PostgreSQL |
| `AISERVICE_URL` | http://ai-service:8000 | Endpoint do AI Service |
| `MODEL_PATH` | ./models/modelo.pth | Caminho do modelo PyTorch |
| `SCALER_PATH` | ./models/scaler.joblib | Caminho do StandardScaler |

## Notas para Desenvolvedores

Para testar localmente sem Docker, rode os servicos individualmente:

```bash
# AI Service
cd ai-service
pip install -r requirements.txt
python src/generate_data.py
python src/train.py
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Backend .NET
cd backend
dotnet restore
dotnet ef database update
dotnet run
```

Para trocar o modelo, basta substituir `ai-service/models/modelo.pth` e reiniciar o container.
