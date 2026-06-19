using CreditScoring.API.Models;
using Microsoft.EntityFrameworkCore;

namespace CreditScoring.API.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Cliente> Clientes => Set<Cliente>();
    public DbSet<Analise> Analises => Set<Analise>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Cliente
        modelBuilder.Entity<Cliente>(entity =>
        {
            entity.ToTable("clientes");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasDefaultValueSql("gen_random_uuid()");
            entity.Property(e => e.Nome).IsRequired().HasMaxLength(150);
            entity.Property(e => e.RendaMensal).HasColumnType("decimal(12,2)");
            entity.Property(e => e.DividaTotal).HasColumnType("decimal(12,2)");
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");
        });

        // Analise
        modelBuilder.Entity<Analise>(entity =>
        {
            entity.ToTable("analises");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasDefaultValueSql("gen_random_uuid()");
            entity.Property(e => e.ScoreRisco).HasColumnType("decimal(5,4)");
            entity.Property(e => e.ProbabilidadeInadimplencia).HasColumnType("decimal(5,4)");
            entity.Property(e => e.ValorSolicitado).HasColumnType("decimal(12,2)");
            entity.Property(e => e.Classificacao).HasMaxLength(20);
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("NOW()");

            entity.HasOne(a => a.Cliente)
                  .WithMany(c => c.Analises)
                  .HasForeignKey(a => a.ClienteId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // Índices
        modelBuilder.Entity<Analise>()
            .HasIndex(a => a.ClienteId)
            .HasDatabaseName("idx_analises_cliente_id");

        modelBuilder.Entity<Analise>()
            .HasIndex(a => a.CreatedAt)
            .HasDatabaseName("idx_analises_created_at");
    }
}
