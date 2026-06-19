namespace CreditScoring.API.Models;

// ──── Requests ────

public record CriarClienteRequest(
    string Nome,
    int Idade,
    decimal RendaMensal,
    int TempoEmpregoMeses,
    decimal DividaTotal,
    int QtdEmprestimos,
    int HistoricoPagamento
);

public record SolicitarAnaliseRequest(
    Guid ClienteId,
    decimal ValorSolicitado
);

// ──── Responses ────

public record ClienteResponse(
    Guid Id,
    string Nome,
    int Idade,
    decimal RendaMensal,
    int TempoEmpregoMeses,
    decimal DividaTotal,
    int QtdEmprestimos,
    int HistoricoPagamento,
    DateTime CreatedAt
);

public record AnaliseResponse(
    Guid Id,
    Guid ClienteId,
    string NomeCliente,
    double ScoreRisco,
    string Classificacao,
    double ProbabilidadeInadimplencia,
    decimal ValorSolicitado,
    bool Aprovado,
    DateTime CreatedAt
);

public record DashboardResponse(
    int TotalAnalises,
    int TotalAprovadas,
    int TotalReprovadas,
    double TaxaAprovacao,
    double ScoreMedio,
    IEnumerable<AnaliseResponse> UltimasAnalises
);

// ──── AI Service ────

public record AiPredictRequest(
    int idade,
    double renda_mensal,
    int tempo_emprego_meses,
    double divida_total,
    int qtd_emprestimos,
    int historico_pagamento,
    double valor_solicitado
);

public record AiPredictResponse(
    double score,
    string classificacao,
    double probabilidade_inadimplencia,
    bool aprovado
);
