using System.Net.Http.Json;
using CreditScoring.API.Models;

namespace CreditScoring.API.Services;

public interface IAiService
{
    Task<AiPredictResponse?> PredictAsync(AiPredictRequest request);
    Task<bool> IsHealthyAsync();
}

public class AiService : IAiService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AiService> _logger;

    public AiService(HttpClient httpClient, ILogger<AiService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<AiPredictResponse?> PredictAsync(AiPredictRequest request)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync("/predict", request);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<AiPredictResponse>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro ao chamar AI Service /predict");
            throw new InvalidOperationException("Serviço de IA indisponível. Tente novamente.", ex);
        }
    }

    public async Task<bool> IsHealthyAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("/health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}
