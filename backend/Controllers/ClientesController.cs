using CreditScoring.API.Data;
using CreditScoring.API.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CreditScoring.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class ClientesController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly ILogger<ClientesController> _logger;

    public ClientesController(AppDbContext db, ILogger<ClientesController> logger)
    {
        _db = db;
        _logger = logger;
    }

    /// <summary>Lista todos os clientes cadastrados.</summary>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<ClienteResponse>), 200)]
    public async Task<IActionResult> GetAll()
    {
        var clientes = await _db.Clientes
            .OrderByDescending(c => c.CreatedAt)
            .Select(c => ToResponse(c))
            .ToListAsync();

        return Ok(clientes);
    }

    /// <summary>Busca cliente por ID.</summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(ClienteResponse), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> GetById(Guid id)
    {
        var cliente = await _db.Clientes.FindAsync(id);
        return cliente is null ? NotFound() : Ok(ToResponse(cliente));
    }

    /// <summary>Cadastra um novo cliente.</summary>
    [HttpPost]
    [ProducesResponseType(typeof(ClienteResponse), 201)]
    [ProducesResponseType(400)]
    public async Task<IActionResult> Create([FromBody] CriarClienteRequest request)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);

        var cliente = new Cliente
        {
            Nome = request.Nome,
            Idade = request.Idade,
            RendaMensal = request.RendaMensal,
            TempoEmpregoMeses = request.TempoEmpregoMeses,
            DividaTotal = request.DividaTotal,
            QtdEmprestimos = request.QtdEmprestimos,
            HistoricoPagamento = request.HistoricoPagamento,
        };

        _db.Clientes.Add(cliente);
        await _db.SaveChangesAsync();

        _logger.LogInformation("Novo cliente cadastrado: {ClienteId} - {Nome}", cliente.Id, cliente.Nome);
        return CreatedAtAction(nameof(GetById), new { id = cliente.Id }, ToResponse(cliente));
    }

    /// <summary>Atualiza dados de um cliente.</summary>
    [HttpPut("{id:guid}")]
    [ProducesResponseType(typeof(ClienteResponse), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Update(Guid id, [FromBody] CriarClienteRequest request)
    {
        var cliente = await _db.Clientes.FindAsync(id);
        if (cliente is null) return NotFound();

        cliente.Nome = request.Nome;
        cliente.Idade = request.Idade;
        cliente.RendaMensal = request.RendaMensal;
        cliente.TempoEmpregoMeses = request.TempoEmpregoMeses;
        cliente.DividaTotal = request.DividaTotal;
        cliente.QtdEmprestimos = request.QtdEmprestimos;
        cliente.HistoricoPagamento = request.HistoricoPagamento;

        await _db.SaveChangesAsync();
        return Ok(ToResponse(cliente));
    }

    /// <summary>Remove um cliente e todas suas análises.</summary>
    [HttpDelete("{id:guid}")]
    [ProducesResponseType(204)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Delete(Guid id)
    {
        var cliente = await _db.Clientes.FindAsync(id);
        if (cliente is null) return NotFound();

        _db.Clientes.Remove(cliente);
        await _db.SaveChangesAsync();
        return NoContent();
    }

    private static ClienteResponse ToResponse(Cliente c) => new(
        c.Id, c.Nome, c.Idade, c.RendaMensal, c.TempoEmpregoMeses,
        c.DividaTotal, c.QtdEmprestimos, c.HistoricoPagamento, c.CreatedAt
    );
}
