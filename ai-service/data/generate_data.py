"""
generate_data.py
Gera um dataset sintético realista de risco de crédito com 20.000 registros.
Simula dados de clientes de um banco e sua classificação de inadimplência.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

N = 20000

# Gera features baseadas em distribuições realistas de dados bancários
idade = np.random.normal(38, 12, N).clip(18, 75).astype(int)
renda_mensal = np.random.lognormal(mean=8.2, sigma=0.6, size=N).clip(1000, 50000)
tempo_emprego_meses = np.random.exponential(48, N).clip(0, 360).astype(int)
divida_total = np.random.lognormal(mean=8.5, sigma=1.2, size=N).clip(0, 300000)
qtd_emprestimos = np.random.randint(0, 8, N)
historico_pagamento = np.random.normal(65, 20, N).clip(0, 100).astype(int)
valor_solicitado = np.random.lognormal(mean=9.5, sigma=0.8, size=N).clip(500, 100000)

# Cálculo de risco baseado em regras de negócio realistas
risco_score = (
    -0.015 * (renda_mensal / 1000)
    + 0.008 * (divida_total / 1000)
    + 0.002 * qtd_emprestimos
    - 0.012 * historico_pagamento
    - 0.003 * (tempo_emprego_meses / 12)
    + 0.005 * (valor_solicitado / 1000)
    + np.random.normal(0, 0.3, N)
)

# Normaliza para probabilidade [0, 1]
risco_min, risco_max = risco_score.min(), risco_score.max()
prob_inadimplente = (risco_score - risco_min) / (risco_max - risco_min)

# Desbalanceia classes como na vida real (~20% inadimplentes)
inadimplente = (prob_inadimplente > 0.72).astype(int)

df = pd.DataFrame({
    "idade": idade,
    "renda_mensal": renda_mensal.round(2),
    "tempo_emprego_meses": tempo_emprego_meses,
    "divida_total": divida_total.round(2),
    "qtd_emprestimos": qtd_emprestimos,
    "historico_pagamento": historico_pagamento,
    "valor_solicitado": valor_solicitado.round(2),
    "inadimplente": inadimplente
})

output_path = os.path.join(os.path.dirname(__file__), "credit_data.csv")
df.to_csv(output_path, index=False)

print(f"✅ Dataset gerado: {len(df)} registros")
print(f"   Adimplentes: {(df['inadimplente'] == 0).sum()} ({(df['inadimplente'] == 0).mean():.1%})")
print(f"   Inadimplentes: {(df['inadimplente'] == 1).sum()} ({(df['inadimplente'] == 1).mean():.1%})")
