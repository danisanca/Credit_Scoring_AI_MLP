using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreditScoring.API.Models;

[Table("clientes")]
public class Cliente
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("nome")]
    [MaxLength(150)]
    public string Nome { get; set; } = string.Empty;

    [Column("idade")]
    public int Idade { get; set; }

    [Column("renda_mensal", TypeName = "decimal(12,2)")]
    public decimal RendaMensal { get; set; }

    [Column("tempo_emprego_meses")]
    public int TempoEmpregoMeses { get; set; }

    [Column("divida_total", TypeName = "decimal(12,2)")]
    public decimal DividaTotal { get; set; }

    [Column("qtd_emprestimos")]
    public int QtdEmprestimos { get; set; }

    [Column("historico_pagamento")]
    public int HistoricoPagamento { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navegação
    public ICollection<Analise> Analises { get; set; } = new List<Analise>();
}
