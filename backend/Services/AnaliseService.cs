using CreditScoring.API.Data;
using CreditScoring.API.Models;
using Microsoft.EntityFrameworkCore;

namespace CreditScoring.API.Services;

public interface IAnaliseService
{
    Task<AnaliseResponse> ExecutarAnaliseAsync(SolicitarAnaliseRequest request);
    Task<IEnumerable<AnaliseResponse>> ListarPorClienteAsync(Guid clienteId);
    Task<IEnumerable<AnaliseResponse>> ListarTodasAsync(int page = 1, int pageSize = 20);
    Task<DashboardResponse> ObterDashboardAsync();
}

public class AnaliseService : IAnaliseService
{
    private readonly AppDbContext _db;
    private readonly IAiService _aiService;
    private readonly ILogger<AnaliseService> _logger;

    public AnaliseService(AppDbContext db, IAiService aiService, ILogger<AnaliseService> logger)
    {
        _db = db;
        _aiService = aiService;
        _logger = logger;
    }

    public async Task<AnaliseResponse> ExecutarAnaliseAsync(SolicitarAnaliseRequest request)
    {
        var cliente = await _db.Clientes.FindAsync(request.ClienteId)
            ?? throw new KeyNotFoundException($"Cliente {request.ClienteId} não encontrado.");

        // Monta request para o AI Service
        var aiRequest = new AiPredictRequest(
            idade: cliente.Idade,
            renda_mensal: (double)cliente.RendaMensal,
            tempo_emprego_meses: cliente.TempoEmpregoMeses,
            divida_total: (double)cliente.DividaTotal,
            qtd_emprestimos: cliente.QtdEmprestimos,
            historico_pagamento: cliente.HistoricoPagamento,
            valor_solicitado: (double)request.ValorSolicitado
        );

        _logger.LogInformation("Chamando AI Service para cliente {ClienteId}", request.ClienteId);
        var aiResult = await _aiService.PredictAsync(aiRequest)
            ?? throw new InvalidOperationException("AI Service retornou resposta inválida.");

        // Persiste a análise no banco
        var analise = new Analise
        {
            ClienteId = cliente.Id,
            ScoreRisco = (decimal)aiResult.score,
            Classificacao = aiResult.classificacao,
            ProbabilidadeInadimplencia = (decimal)aiResult.probabilidade_inadimplencia,
            ValorSolicitado = request.ValorSolicitado,
            Aprovado = aiResult.aprovado,
        };

        _db.Analises.Add(analise);
        await _db.SaveChangesAsync();

        _logger.LogInformation(
            "Análise {AnaliseId} criada: Score={Score}, Risco={Risco}, Aprovado={Aprovado}",
            analise.Id, analise.ScoreRisco, analise.Classificacao, analise.Aprovado
        );

        return MapToResponse(analise, cliente.Nome);
    }

    public async Task<IEnumerable<AnaliseResponse>> ListarPorClienteAsync(Guid clienteId)
    {
        return await _db.Analises
            .Include(a => a.Cliente)
            .Where(a => a.ClienteId == clienteId)
            .OrderByDescending(a => a.CreatedAt)
            .Select(a => MapToResponse(a, a.Cliente!.Nome))
            .ToListAsync();
    }

    public async Task<IEnumerable<AnaliseResponse>> ListarTodasAsync(int page = 1, int pageSize = 20)
    {
        return await _db.Analises
            .Include(a => a.Cliente)
            .OrderByDescending(a => a.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(a => MapToResponse(a, a.Cliente!.Nome))
            .ToListAsync();
    }

    public async Task<DashboardResponse> ObterDashboardAsync()
    {
        var total = await _db.Analises.CountAsync();
        var aprovadas = await _db.Analises.CountAsync(a => a.Aprovado);
        var scoreMedio = total > 0
            ? (double)await _db.Analises.AverageAsync(a => a.ScoreRisco)
            : 0.0;

        var ultimas = await _db.Analises
            .Include(a => a.Cliente)
            .OrderByDescending(a => a.CreatedAt)
            .Take(10)
            .Select(a => MapToResponse(a, a.Cliente!.Nome))
            .ToListAsync();

        return new DashboardResponse(
            TotalAnalises: total,
            TotalAprovadas: aprovadas,
            TotalReprovadas: total - aprovadas,
            TaxaAprovacao: total > 0 ? Math.Round((double)aprovadas / total * 100, 1) : 0,
            ScoreMedio: Math.Round(scoreMedio * 100, 1),
            UltimasAnalises: ultimas
        );
    }

    private static AnaliseResponse MapToResponse(Analise a, string nomeCliente) => new(
        Id: a.Id,
        ClienteId: a.ClienteId,
        NomeCliente: nomeCliente,
        ScoreRisco: Math.Round((double)a.ScoreRisco * 100, 1),
        Classificacao: a.Classificacao,
        ProbabilidadeInadimplencia: Math.Round((double)a.ProbabilidadeInadimplencia * 100, 1),
        ValorSolicitado: a.ValorSolicitado,
        Aprovado: a.Aprovado,
        CreatedAt: a.CreatedAt
    );
}
