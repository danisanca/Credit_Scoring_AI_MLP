using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreditScoring.API.Models;

[Table("analises")]
public class Analise
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("cliente_id")]
    public Guid ClienteId { get; set; }

    [Column("score_risco", TypeName = "decimal(5,4)")]
    public decimal ScoreRisco { get; set; }

    [Column("classificacao")]
    [MaxLength(20)]
    public string Classificacao { get; set; } = string.Empty;

    [Column("probabilidade_inadimplencia", TypeName = "decimal(5,4)")]
    public decimal ProbabilidadeInadimplencia { get; set; }

    [Column("valor_solicitado", TypeName = "decimal(12,2)")]
    public decimal ValorSolicitado { get; set; }

    [Column("aprovado")]
    public bool Aprovado { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navegação
    [ForeignKey("ClienteId")]
    public Cliente? Cliente { get; set; }
}
