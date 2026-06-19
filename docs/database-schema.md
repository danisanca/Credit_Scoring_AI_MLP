# Documentacao do Banco de Dados — Credit Scoring AI

## Visao Geral

O PostgreSQL armazena o historico de analises de credito realizadas pelo sistema. Cada vez que um usuario preenche o formulario e clica em "Analisar", um registro e salvo no banco com o resultado da predicao.

Isso permite:
- Auditoria de decisoes
- Dashboard com metricas historicas
- Rastreamento de tendencias (taxa de aprovacao ao longo do tempo)

## Schema

### Tabela: `CreditAnalises`

| Coluna | Tipo | Constraints | Descricao |
|--------|------|-------------|-----------|
| `Id` | int | PK, AutoIncrement | Identificador unico |
| `Cliente` | varchar(200) | Not Null | Nome do cliente |
| `Idade` | int | >= 18, <= 70 | Idade na data da analise |
| `RendaMensal` | decimal(10,2) | >= 0 | Renda mensal em R$ |
| `TempoEmpregoMeses` | int | >= 0 | Meses no emprego |
| `DividaTotal` | decimal(12,2) | >= 0 | Total de dividas |
| `QtdEmprestimos` | int | >= 0 | Emprestimos ativos |
| `HistoricoPagamento` | int | 0, 1 ou 2 | Score de pagamento |
| `ValorSolicitado` | decimal(12,2) | >= 0 | Valor do pedido |
| `Score` | decimal(5,4) | 0-1 | Probabilidade de inadimplencia |
| `Limiar` | decimal(3,2) | Default 0.5 | Threshold de decisao |
| `Decisao` | varchar(50) | Not Null | APROVADO/REPROVADO |
| `DataAnalise` | timestamp | Default NOW() | Data da analise |

### Enum/Tipos

```csharp
public enum StatusDecisao
{
    APROVADO,
    REPROVADO
}

public enum Risco
{
    BAIXO,    // Score < 0.30
    MEDIO,    // Score 0.30-0.70
    ALTO      // Score > 0.70
}
```

## Diagrama ER (Simplificado)

```
+-------------------------+
|    CreditAnalises       |
+-------------------------+
| PK  Id                  |
|     Cliente             |
|     Idade               |
|     RendaMensal         |
|     TempoEmpregoMeses   |
|     DividaTotal         |
|     QtdEmprestimos      |
|     HistoricoPagamento  |
|     ValorSolicitado     |
|     Score               |
|     Limiar              |
|     Decisao             |
|     DataAnalise         |
+-------------------------+
```

## Queries Uteis

### Taxa de aprovacao total
```sql
SELECT
    ROUND(
        COUNT(*) FILTER (WHERE "Decisao" = 'APROVADO')::decimal /
        COUNT(*) * 100,
        2
    ) AS taxa_aprovacao
FROM "CreditAnalises";
```

### Media de score por mes
```sql
SELECT
    DATE_TRUNC('month', "DataAnalise") AS mes,
    ROUND(AVG("Score"), 4) AS media_score,
    COUNT(*) AS total_analises
FROM "CreditAnalises"
GROUP BY mes
ORDER BY mes DESC;
```

### Maiores riscos do ultimo dia
```sql
SELECT
    "Cliente",
    "Score",
    "Decisao",
    "DataAnalise"
FROM "CreditAnalises"
WHERE "Score" > 0.70
  AND "DataAnalise" >= CURRENT_DATE - INTERVAL '1 day'
ORDER BY "Score" DESC
LIMIT 10;
```

### Distribuicao de scores (bins)
```sql
SELECT
    CASE
        WHEN "Score" < 0.25 THEN 'Muito Baixo (0-0.25)'
        WHEN "Score" < 0.50 THEN 'Baixo (0.25-0.50)'
        WHEN "Score" < 0.75 THEN 'Medio (0.50-0.75)'
        ELSE 'Alto (0.75-1.00)'
    END AS faixa_risco,
    COUNT(*) AS quantidade
FROM "CreditAnalises"
GROUP BY faixa_risco;
```

## Migracao e Seed

O backend usa Entity Framework Core com migracoes automatizadas. Ao subir o Docker Compose, o entrypoint executa:

```bash
dotnet ef database update --context CreditContext
```

Isso cria automaticamente a tabela `CreditAnalises` com todos os indexes.

Nao existe seed automatico (dados iniciais), pois o banco e populado naturalmente a medida que os usuarios fazem analises pelo frontend.

## Backup

Em producao, recomendo configurar backups diarios via `pg_dump`:

```bash
pg_dump -h db -U agente_user -Fc credit_scoring_db > backup_$(date +%Y%m%d).dump
```

Para restaurar:
```bash
pg_restore -h db -U agente_user -d credit_scoring_db backup_20260115.dump
```

## Volume Docker

O banco persiste em um volume Docker nomeado:

```yaml
volumes:
  postgres_data:
    driver: local
```

Isso garante que os dados nao sejam perdidos quando o container e reiniciado.

## Indicadores de Performance

Considerando o volume esperado (~100 analises/dia), o PostgreSQL com um unico indice na chave primaria e mais que suficiente. Se o volume crescer para milhoes de registros, adicione indexes em:

- `DataAnalise` (queries por periodo)
- `Decisao` (queries de aprovacao/reprovacao)
- `Score` (queries de maior risco)

## Contato

Autor: [danisanca](https://github.com/danisanca)

