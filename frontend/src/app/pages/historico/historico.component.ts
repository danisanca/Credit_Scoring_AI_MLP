import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, AnaliseResponse } from '../../services/api.service';

@Component({
  selector: 'app-historico',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="historico">
      <h2>Histórico Completo de Análises</h2>
      <p class="text-muted mb-4">Todas as inferências executadas pela rede neural no banco de dados.</p>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>ID Cliente (UUID)</th>
              <th>Nome</th>
              <th>Score Estimado</th>
              <th>Probabilidade de Calote</th>
              <th>Classificação</th>
              <th>Decisão Final</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let item of analises">
              <td class="text-muted">{{ item.createdAt | date:'short' }}</td>
              <td class="text-muted" style="font-size: 12px">{{ item.clienteId }}</td>
              <td style="font-weight: 600">{{ item.nomeCliente }}</td>
              <td>{{ item.scoreRisco }}</td>
              <td>{{ item.probabilidadeInadimplencia }}%</td>
              <td>
                <span class="badge" [ngClass]="item.classificacao.toLowerCase()">
                  {{ item.classificacao }}
                </span>
              </td>
              <td>
                <span *ngIf="item.aprovado" class="text-success" style="font-weight: 600">APROVADO</span>
                <span *ngIf="!item.aprovado" class="text-danger" style="font-weight: 600">NEGADO</span>
              </td>
            </tr>
            <tr *ngIf="analises.length === 0">
              <td colspan="7" style="text-align: center; padding: 32px;" class="text-muted">
                Nenhuma análise encontrada no banco de dados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .historico { display: flex; flex-direction: column; }
    .mb-4 { margin-bottom: 24px; }
    
    .table-container { background: var(--bg-secondary); border-radius: 12px; overflow: hidden; border: 1px solid var(--bg-tertiary); }
    .data-table { width: 100%; border-collapse: collapse; text-align: left; }
    .data-table th, .data-table td { padding: 16px 24px; border-bottom: 1px solid var(--bg-tertiary); }
    .data-table th { color: var(--text-secondary); font-weight: 600; font-size: 14px; text-transform: uppercase; }
    .data-table tr:hover { background: rgba(255,255,255,0.02); }
    
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge.baixo { background: rgba(34, 197, 94, 0.1); color: var(--success); }
    .badge.médio { background: rgba(245, 158, 11, 0.1); color: var(--warning); }
    .badge.alto { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
  `]
})
export class HistoricoComponent implements OnInit {
  analises: AnaliseResponse[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getHistorico().subscribe({
      next: (res) => this.analises = res,
      error: (err) => console.error('Erro ao buscar histórico', err)
    });
  }
}
