# Credit Scoring AI — Projeto de Portfólio Fullstack

Um sistema completo de Inteligência Artificial para análise de risco de crédito (Credit Scoring) projetado para nível de produção, com arquitetura em microsserviços.

Este projeto faz parte do portfólio profissional de IA, demonstrando habilidade em construir o fluxo ponta a ponta: do pré-processamento de dados até uma API servindo uma Rede Neural conectada a um sistema web complexo.

## 🏗️ Arquitetura

O sistema é dividido em 3 camadas orquestradas via **Docker Compose**:

1. **Frontend (Angular 17):** Single Page Application com Dashboard financeiro "Dark Mode", gráfico de medidor de risco e tabelas de histórico.
2. **Backend BFF (C# .NET 8):** API robusta com Entity Framework Core que salva as requisições em banco de dados relacional e consome o serviço de IA de forma segura.
3. **AI Service (Python FastAPI + PyTorch):** Microsserviço de Inteligência Artificial. Implementa uma MLP (Multi-Layer Perceptron) que recebe os dados do cliente e prediz a probabilidade de inadimplência.

## 🚀 Como Executar

### Pré-requisitos
- Docker e Docker Compose instalados na máquina.

### Passos
1. Clone este repositório.
2. Na raiz da pasta `credit-scoring-ai`, execute:
   ```bash
   docker-compose up --build
   ```
3. O Docker fará o download das imagens, criará o dataset sintético de 20.000 registros, treinará a Rede Neural na hora e subirá a API C# e o Frontend Angular.

### Acessos Locais:
- **Frontend (Painel Angular):** http://localhost:4200
- **Backend Swagger (C# API):** http://localhost:5000/swagger
- **AI Service Docs (FastAPI):** http://localhost:8000/docs
- **Banco de Dados GUI (pgAdmin):** http://localhost:5050 (Login: `admin@creditscoring.com` / Senha: `admin123`)

## 🧠 Foco Técnico e Desafios Resolvidos

* **Dataset Sintético:** O projeto possui um gerador de dados estocástico que simula regras de negócios de banco para garantir que o projeto funcione localmente sem depender de arquivos pesados externos.
* **Desbalanceamento de Classes:** Redes Neurais sofrem quando 80% dos dados dizem que os clientes são "Bons pagadores". Para resolver isso, usamos os `class_weights` dentro da Loss Function (`BCEWithLogitsLoss`) no PyTorch.
* **Early Stopping e Checkpoint:** O script de treino (`src/train.py`) monitora o F1-Score da validação. Quando o modelo para de aprender, o treino é cortado prematuramente e apenas os melhores "pesos" (`.pth`) são exportados para produção, evitando overfitting.
* **StandardScaler na API:** Para garantir a integridade dos dados, o mesmo scaler matematicamente usado para normalizar os dados do treinamento é salvo com `joblib` e carregado pela FastAPI na hora da inferência.
