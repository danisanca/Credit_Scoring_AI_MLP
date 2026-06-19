# Documentacao do Modelo — Credit Scoring MLP

## Objetivo

Prever a probabilidade de um cliente se tornar inadimplente com base em 7 variaveis socioeconomicas. O resultado e um numero entre 0 e 1, que e transformado em uma decisao binaria (APROVADO/REPROVADO) via threshold.

## Arquitetura da Rede Neural

### Tipo: Multi-Layer Perceptron (MLP)

```
Input Layer (7 features)
    |
    v
Hidden Layer 1: Linear(7, 64) --> BatchNorm1d(64) --> ReLU --> Dropout(0.3)
    |
    v
Hidden Layer 2: Linear(64, 32) --> BatchNorm1d(32) --> ReLU --> Dropout(0.3)
    |
    v
Hidden Layer 3: Linear(32, 16) --> BatchNorm1d(16) --> ReLU --> Dropout(0.15)
    |
    v
Output Layer: Linear(16, 1) --> Sigmoid()
```

### Por que essa arquitetura?

Escolhi progressiveamente reduzir o numero de neuronios (64 → 32 → 16) para forcar a rede a aprender representacoes compactas e relevantes. Isso e uma forma implicita de regularizacao: quanto mais estreitas as camadas, menor a chance de overfitting.

### Batch Normalization

Coloquei BatchNorm apos cada Linear para estabilizar o treinamento. Sem BN, os gradientes explodem rapidamente em redes de mais de 2 camadas com ReLU. A BN normaliza os inputs de cada camada em tempo de execucao, acelerando a convergencia e permitindo learning rates maiores.

### Dropout

Dropout de 30% nas duas primeiras camadas e 15% na ultima oculta. Isso forca a rede a nao depender de um unico neuronio e aprender redundancias. A taxa decrescente (30% → 15%) reflete que a ultima camada precisa de menos regularizacao porque ja esta mais proxima da decisao final.

### Funcao de Ativacao: ReLU

ReLU escolhida sobre Tanh ou LeakyReLU porque:
- Evita o vanishing gradient problem
- Computacionalmente mais barata
- Funciona bem com BatchNorm

Na saida, usei Sigmoid para converter logits em probabilidade interpretavel (0-1).

## Features de Entrada

| Feature | Tipo | Range | Descricao |
|---------|------|-------|-----------|
| idade | int | 18-70 | Idade do cliente |
| renda_mensal | float | R$ 1.200 - R$ 25.000 | Renda liquida mensal |
| tempo_emprego_meses | int | 0-360 | Tempo no emprego atual |
| divida_total | float | R$ 0 - R$ 150.000 | Somatorio de todas as dividas |
| qtd_emprestimos | int | 0-10 | Numero de emprestimos ativos |
| historico_pagamento | int | 0-2 | 0=Bom, 1=Regular, 2=Ruim |
| valor_solicitado | float | R$ 500 - R$ 50.000 | Valor do emprestimo solicitado |

### Feature Engineering

Alem das features brutas, apliquei:

- **StandardScaler:** Todas as features sao normalizadas para media 0 e desvio padrao 1. Isso e crucial porque PyTorch SGD converge mal com features em escalas diferentes (renda_mensal em milhares vs historico_pagamento em unidades).
- **Target Encoding (implicito):** Nao usei target encoding para evitar leakage; apenas o StandardScaler e suficiente.

## Treinamento

### Perda: BCEWithLogitsLoss

Usei Binary Cross Entropy combinada com Logits em vez de BCE puro porque:
- Numericamente mais estavel (a funcao combina sigmoid + BCE em uma unica operacao)
- Permite usar `class_weights` diretamente no loss function

### Otimizador: Adam

Learning rate = 1e-3, betas default. Adam foi escolhido porque:
- Automaticamente ajusta o learning rate por parametro
- Funciona bem com BatchNorm
- Nao precisa de learning rate scheduling manual

### Class Weighting

O dataset e desbalanceado: ~80% bons pagadores. Sem pesos, o modelo aprenderia a sempre dizer "nao inadimplente" e teria 80% de acuracia por coincidencia.

Calculei o peso da classe minoritaria como:
```python
weight = n_majority / n_minority  # ~4.0
loss_fn = BCEWithLogitsLoss(pos_weight=torch.tensor([weight]))
```

Isso penaliza erros da classe "inadimplente" 4x mais fortemente, forçando o modelo a aprender a diferenciar os dois grupos.

### Early Stopping

Monitoro o F1-Score de validacao a cada epoca. Se o F1 nao melhora por 15 epocas consecutivas, o treinamento e abortado e o melhor checkpoint e salvo.

**Por que F1 e nao Accuracy?**
Accuracy e enganosa em datasets desbalanceados. Um modelo que preve "tudo 0" acerta 80% sem aprender nada. F1 combina Precision e Recall e da peso igual aos dois erros (falso positivo e falso negativo).

### Metricas de Avaliacao

Após o treinamento, o `evaluate.py` calcula:
- **ROC-AUC:** Area sob a curva ROC (ideal > 0.80)
- **F1-Score:** Harmonica entre Precision e Recall
- **Confusion Matrix:** Para visualizar falsos positivos/negativos

### Hiperparametros

| Parametro | Valor | Justificativa |
|-----------|-------|---------------|
| input_size | 7 | Numero de features |
| hidden_dims | [64, 32, 16] | Representacao progressivamente compacta |
| dropout_rate | 0.3 (entrada/meio), 0.15 (final) | Regularizacao decrescente |
| learning_rate | 1e-3 | Padrao para Adam, convergiu rapido |
| batch_size | 64 | Equilibrio entre velocidade e estabilidade |
| epochs_max | 200 | Limite de seguranca, early stopping corta antes |
| patience | 15 | Equilibrio entre tempo de treino e overfitting |

## Limitacoes e Consideracoes Eticas

Este e um modelo **sintetico** treinado com dados ficticios. Em producao real, seria necessario:

- **Auditoria de vies:** Verificar se o modelo discrimina grupos raciais, de genero ou regionais
- **Explicabilidade:** Implementar SHAP ou LIME para justificar cada decisao individual
- **Revisao humana:** Qualquer decisao automatica de credito deve ter recurso humano em paises como o Brasil (Lei 14.010/2020)
- **Re-treino periodico:** Dados financeiros envelhecem rapidamente; o modelo deve ser re-treinado trimestralmente

## Artigos e Referencias

- Goodfellow, I. et al. "Deep Learning". MIT Press, 2016. (Cap. 6: MLP)
- Kingma, D.P. & Ba, J. "Adam: A Method for Stochastic Optimization". ICLR, 2015.
- He, K. et al. "Delving Deep into Rectifiers". ICCV, 2015. (BatchNorm)
- Srivastava, N. et al. "Dropout: A Simple Way to Prevent Neural Networks from Overfitting". JMLR, 2014.

## Autor

[danisanca](https://github.com/danisanca)

