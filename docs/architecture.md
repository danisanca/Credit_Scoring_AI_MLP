# Documentacao Tecnica — Arquitetura do Credit Scoring AI

## Visao Geral

Este projeto foi concebido como um sistema completo de ponta a ponta para analise de risco de credito, combinando Machine Learning, Engenharia de Software e DevOps em uma unica solucao.

A motivacao central foi criar um portfolio que demonstre minha capacidade de nao apenas treinar um modelo, mas tambem de integra-lo em um ecossistema produtivo com APIs, banco de dados e interface web.

## Diagrama de Componentes

```
+---------------------------------------------------+
|  Cliente (Browser)                                 |
|  - Angular 17 SPA                                  |
|  - Dark mode dashboard                             |
|  - Recharts para visualizacao                      |
+---------------------------------------------------+
                       |
                       v HTTP/JSON
+---------------------------------------------------+
|  Frontend Nginx (Porta 4200)                      |
|  - Serve SPA estatico                              |
|  - Proxy reverso para API                          |
+---------------------------------------------------+
                       |
                       v
+---------------------------------------------------+
|  Backend .NET 8 (Porta 5000)                       |
|  - Controllers REST                                |
|  - Entity Framework Core + PostgreSQL               |
|  - HttpClient para IA Service                      |
+---------------------------------------------------+
                       |
                       v
+---------------------------------------------------+
|  AI Service FastAPI (Porta 8000)                  |
|  - /predict: inferencia em tempo real             |
|  - /health: healthcheck                          |
|  - PyTorch MLP carregado em memoria               |
+---------------------------------------------------+
```

## Fluxo de Dados

### 1. Treinamento (One-shot)

Quando o container do AI Service sobe pela primeira vez, o entrypoint executa:

```
generate_data.py --> credit_dataset.csv (20.000 registros)
     |
     v
dataset.py --load_and_split()--> train_loader, val_loader, test_loader
     |
     v
train.py --> modelo.pth + scaler.joblib
```

Os artefatos gerados (`modelo.pth` e `scaler.joblib`) sao salvos no volume Docker e reutilizados em todas as inferencias subsequentes.

### 2. Inferencia (Tempo Real)

```
Usuario preenche formulario (Angular)
       |
       v POST /api/analises
Backend .NET valida e persiste no PostgreSQL
       |
       v GET ai-service:8000/predict?id_cliente=123
AI Service carrega modelo.pth e scaler.joblib
       |
       v
PyTorch MLP faz forward pass
       |
       v JSON {probabilidade, limiar, decisao}
Backend atualiza registro com resultado
       |
       v JSON {id, probabilidade, decisao, risco}
Angular renderiza gauge e badge de status
```

## Decisoes de Design

### Por que 3 camadas?

Separei em 3 servicos para cumprir o principio de responsabilidade unica:

1. **Angular:** Apenas UI e UX. Nao sabe da existencia do modelo PyTorch.
2. **.NET Backend:** Orquestracao, persistencia, validacao e seguranca.
3. **AI Service:** Logica pura de inferencia. Sem acesso ao banco, sem estado.

Isso permite que cada camada escale de forma independente. Se o trafego de previsoes aumentar, posso escalar apenas o AI Service sem tocar no frontend ou no banco.

### Por que PostgreSQL?

Embora o dataset sintetico ja exista em CSV, o PostgreSQL armazena o **historico de decisoes**. Isso permite:
- Auditoria: "Por que esse cliente foi negado na data X?"
- Analytics: taxa de inadimplencia prevista vs real ao longo do tempo
- Dashboard: ranking de maiores riscos

### Por que FastAPI em vez de Flask?

A geracao automatica de OpenAPI/Swagger foi o fator decisivo. Tambem gosto do suporte nativo a Pydantic para validacao de entrada, que reduz drasticamente o risco de bugs de tipagem.

## Proximos Passos (Roadmap)

- [ ] Adicionar autenticacao JWT para proteger os endpoints
- [ ] Implementar fila (Redis/RabbitMQ) para processamento assincrono de batch
- [ ] Adicionar explicabilidade (SHAP ou LIME) para justificar cada decisao
- [ ] Criar notebook EDA com analise exploratoria detalhada
- [ ] Deploy em cloud (AWS/GCP) com Kubernetes

## Contato

Autor: [danisanca](https://github.com/danisanca)
