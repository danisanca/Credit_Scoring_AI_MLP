using CreditScoring.API.Models;
using CreditScoring.API.Services;
using Microsoft.AspNetCore.Mvc;

namespace CreditScoring.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class AnalisesController : ControllerBase
{
    private readonly IAnaliseService _analiseService;
    private readonly IAiService _aiService;
    private readonly ILogger<AnalisesController> _logger;

    public AnalisesController(IAnaliseService analiseService, IAiService aiService, ILogger<AnalisesController> logger)
    {
        _analiseService = analiseService;
        _aiService = aiService;
        _logger = logger;
    }

    /// <summary>Solicita uma nova análise de crédito para um cliente.</summary>
    [HttpPost]
    [ProducesResponseType(typeof(AnaliseResponse), 201)]
    [ProducesResponseType(400)]
    [ProducesResponseType(404)]
    [ProducesResponseType(503)]
    public async Task<IActionResult> SolicitarAnalise([FromBody] SolicitarAnaliseRequest request)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);

        try
        {
            var resultado = await _analiseService.ExecutarAnaliseAsync(request);
            _logger.LogInformation("Análise concluída: {AnaliseId}", resultado.Id);
            return CreatedAtAction(nameof(GetById), new { id = resultado.Id }, resultado);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            return StatusCode(503, new { message = ex.Message });
        }
    }

    /// <summary>Busca análise por ID.</summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(AnaliseResponse), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> GetById(Guid id)
    {
        var analises = await _analiseService.ListarTodasAsync(1, 1000);
        var analise = analises.FirstOrDefault(a => a.Id == id);
        return analise is null ? NotFound() : Ok(analise);
    }

    /// <summary>Lista todas as análises com paginação.</summary>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<AnaliseResponse>), 200)]
    public async Task<IActionResult> GetAll([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var analises = await _analiseService.ListarTodasAsync(page, pageSize);
        return Ok(analises);
    }

    /// <summary>Lista análises de um cliente específico.</summary>
    [HttpGet("cliente/{clienteId:guid}")]
    [ProducesResponseType(typeof(IEnumerable<AnaliseResponse>), 200)]
    public async Task<IActionResult> GetByCliente(Guid clienteId)
    {
        var analises = await _analiseService.ListarPorClienteAsync(clienteId);
        return Ok(analises);
    }

    /// <summary>Retorna dados agregados para o Dashboard.</summary>
    [HttpGet("dashboard")]
    [ProducesResponseType(typeof(DashboardResponse), 200)]
    public async Task<IActionResult> GetDashboard()
    {
        var dashboard = await _analiseService.ObterDashboardAsync();
        return Ok(dashboard);
    }

    /// <summary>Verifica status do serviço de IA.</summary>
    [HttpGet("ai-health")]
    public async Task<IActionResult> AiHealth()
    {
        var isHealthy = await _aiService.IsHealthyAsync();
        return isHealthy
            ? Ok(new { status = "AI Service online" })
            : StatusCode(503, new { status = "AI Service offline" });
    }
}
