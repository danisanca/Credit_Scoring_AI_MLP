# Credit Scoring AI — Projeto de Portfolio Fullstack

Um sistema completo de Inteligencia Artificial para analise de risco de credito (Credit Scoring), projetado para nivel de producao, com arquitetura em microsservicos.

Eu construi este projeto do zero para demonstrar minha capacidade de criar o fluxo ponta a ponta: desde o pre-processamento de dados, o treinamento de uma rede neural profunda, ate a deploy via Docker em uma API REST conectada a um painel web moderno.

[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![.NET](https://img.shields.io/badge/.NET-8.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![Angular](https://img.shields.io/badge/Angular-17-DD0031?logo=angular&logoColor=white)](https://angular.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3+-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/danisanca/Credit_Scoring_AI_MLP/ci.yml?label=CI%20Build)](https://github.com/danisanca/Credit_Scoring_AI_MLP/actions)

## Screenshots

### Dashboard — Visao Geral do Risco
> Screenshot AQUI !!!

### Nova Analise de Credito
> Screenshot AQUI !!!

### Resultado da Predicao com Gauge de Risco
> Screenshot AQUI !!!

### Tabela de Historico com Scores
> Screenshot AQUI !!!

## Arquitetura

Eu desenhei o sistema com 3 camadas independentes, orquestradas via **Docker Compose** para facilitar o deploy local:

1. **Frontend (Angular 17):** SPA com dashboard financeiro no estilo "Dark Mode", graficos de medidor de risco dinamicos e tabela de historico. Implementei roteamento lazy-loading para performance.
2. **Backend BFF (C# .NET 8):** API RESTful com Entity Framework Core e PostgreSQL. Ele persiste cada analise solicitada e atua como camada de protecao, expondo os endpoints de forma segura para o Angular consumir.
3. **AI Service (Python FastAPI + PyTorch):** Microsservico dedicado a IA. Treinei uma MLP (Multi-Layer Perceptron) com 3 camadas ocultas e apliquei tecnicas como early stopping, BatchNorm e Dropout para evitar overfitting.

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Angular   │ ───▶ │ .NET 8 API   │ ───▶ │ FastAPI AI  │
│  (4200)     │ ◀─── │   (5000)     │ ◀─── │   (8000)    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │    (5432)    │
                     └──────────────┘
```

## Como Executar

### Pre-requisitos
- Docker e Docker Compose instalados.

### Passos
1. Clone o repositorio:
   ```bash
   git clone https://github.com/danisanca/Credit_Scoring_AI_MLP.git
   cd Credit_Scoring_AI_MLP
   ```
2. Suba todos os servicos:
   ```bash
   docker-compose up --build
   ```
   Isso vai gerar o dataset sintetico, treinar o modelo e subir tudo automaticamente.

### Acessos Locais
| Servico | URL |
|---------|-----|
| Frontend (Angular) | http://localhost:4200 |
| Backend Swagger | http://localhost:5000/swagger |
| AI Service Docs | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 (admin@creditscoring.com / admin123) |

## Desafios Tecnicos que Resolvi

### Dataset Sintetico Realista
Como nao tinha acesso a dados reais de clientes, criei um gerador estocastico em Python que simula distribuicoes estatisticas realisticas para renda, idade, tempo de emprego e divida total. Isso garante que qualquer pessoa possa rodar o projeto localmente sem depender de bases privadas.

### Desbalanceamento de Classes (Imbalanced Dataset)
O maior desafio foi que aproximadamente 80% dos registros representam bons pagadores. Um modelo ingenuo poderia acertar 80% apenas dizendo "nao inadimplente" sempre. Eu resolvi isso usando:
- `class_weights` dentro da funcao de perda `BCEWithLogitsLoss` para penalizar mais o erro da classe minoritaria
- SMOTE nao foi necessario porque o gerador permite controle direto da proporcao de classes

### Early Stopping e Checkpoint de Pesos
O treinamento monitora o F1-Score de validacao a cada epoca. Quando o modelo para de melhorar (plateau), o treino e interrompido e apenas os melhores pesos (`.pth`) sao exportados. Isso evita overfitting e economiza tempo de treino.

### StandardScaler Persistente
Para garantir consistencia entre treino e producao, o mesmo `StandardScaler` usado durante o treinamento e salvo com `joblib` e carregado pela FastAPI na hora da inferencia. Sem isso, os inputs no ambiente de producao teriam normalizacao diferente, invalidando o modelo.

### Padronizacao de Decisoes
Na logica de negocios, defini limites claros:
- **Probabilidade < 0.30:** Aprovado automaticamente
- **Probabilidade 0.30-0.70:** Analise humana necessaria
- **Probabilidade > 0.70:** Negado automaticamente

Isso transforma o score numerico bruto em uma decisao acionavel para o usuario final.

## Stack Tecnologica

| Camada | Tecnologias |
|--------|-------------|
| Frontend | Angular 17, TypeScript, SCSS, RxJS |
| Backend | .NET 8, EF Core, PostgreSQL, Swagger |
| AI / ML | Python 3.11, FastAPI, PyTorch 2.3, scikit-learn |
| Infra | Docker, Docker Compose, Nginx |

## Estrutura do Projeto

```
credit-scoring-ai/
├── ai-service/          # Python FastAPI + PyTorch
│   ├── src/             # train.py, model.py, dataset.py, evaluate.py
│   ├── api/             # main.py (endpoints FastAPI)
│   ├── data/            # Gerador de dataset sintetico
│   └── models/          # Pesos (.pth) e scaler serializado
├── backend/             # C# .NET 8 API
│   ├── Controllers/
│   ├── Models/
│   ├── Services/
│   └── appsettings.json
├── frontend/            # Angular 17 SPA
│   ├── src/app/         # Components, services, models
│   └── nginx.conf       # Configuracao de producao
├── docs/                # Documentacao tecnica
│   ├── architecture.md
│   ├── api.md
│   ├── model.md
│   └── database-schema.md
├── .github/workflows/   # CI/CD pipeline
│   └── ci.yml
├── docker-compose.yml
├── README.md
└── LICENSE
```

## Pipeline CI/CD

O projeto conta com um pipeline GitHub Actions que executa a cada Pull Request e merge na branch `main`:
- Build das imagens Docker (frontend, backend, AI service)
- Execucao dos testes unitarios do Python (pytest)
- Validacao do formato do codigo C# e TypeScript
- Verificacao de build sem erros

Voce pode acompanhar o status no badge de build acima.

## Licenca

Este projeto e licenciado sob a MIT License. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

Me encontre no [LinkedIn](https://linkedin.com/in/seu-perfil) ou [GitHub](https://github.com/danisanca).

