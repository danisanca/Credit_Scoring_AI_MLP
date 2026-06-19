import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { ApiService, DashboardResponse } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  template: `
    <div class="dashboard" *ngIf="data">
      <div class="header">
        <h1>Visão Geral de Crédito</h1>
        <p class="text-muted">Resumo de análises executadas pelo modelo de Inteligência Artificial</p>
      </div>

      <div class="kpi-grid">
        <mat-card class="kpi-card">
          <mat-card-content>
            <div class="kpi-header">
              <span class="text-muted">Total de Análises</span>
              <mat-icon color="primary">assignment</mat-icon>
            </div>
            <h2>{{ data.totalAnalises }}</h2>
          </mat-card-content>
        </mat-card>

        <mat-card class="kpi-card">
          <mat-card-content>
            <div class="kpi-header">
              <span class="text-muted">Taxa de Aprovação</span>
              <mat-icon class="text-success">check_circle</mat-icon>
            </div>
            <h2 class="text-success">{{ data.taxaAprovacao }}%</h2>
          </mat-card-content>
        </mat-card>

        <mat-card class="kpi-card">
          <mat-card-content>
            <div class="kpi-header">
              <span class="text-muted">Reprovações (Risco)</span>
              <mat-icon class="text-danger">cancel</mat-icon>
            </div>
            <h2 class="text-danger">{{ data.totalReprovadas }}</h2>
          </mat-card-content>
        </mat-card>

        <mat-card class="kpi-card">
          <mat-card-content>
            <div class="kpi-header">
              <span class="text-muted">Score Médio</span>
              <mat-icon class="text-warning">speed</mat-icon>
            </div>
            <h2>{{ data.scoreMedio }} <span style="font-size: 14px">/ 100</span></h2>
          </mat-card-content>
        </mat-card>
      </div>

      <h2 style="margin-top: 40px; margin-bottom: 20px;">Últimas Análises Processadas</h2>
      
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Valor Solicitado</th>
              <th>Classificação IA</th>
              <th>Score (Confiança)</th>
              <th>Status Final</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let item of data.ultimasAnalises">
              <td>{{ item.nomeCliente }}</td>
              <td>{{ item.valorSolicitado | currency:'BRL' }}</td>
              <td>
                <span class="badge" [ngClass]="item.classificacao.toLowerCase()">
                  {{ item.classificacao }} Risco
                </span>
              </td>
              <td>{{ item.scoreRisco }}</td>
              <td>
                <span *ngIf="item.aprovado" class="text-success" style="font-weight: 600">APROVADO</span>
                <span *ngIf="!item.aprovado" class="text-danger" style="font-weight: 600">NEGADO</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .dashboard { display: flex; flex-direction: column; gap: 24px; }
    .header h1 { font-size: 28px; margin-bottom: 8px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; }
    .kpi-header { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; margin-bottom: 12px; font-weight: 500; }
    .kpi-header span { font-size: 13px; color: var(--text-secondary); word-break: break-word; overflow-wrap: break-word; line-height: 1.3; }
    .kpi-header mat-icon { font-size: 20px; width: 20px; height: 20px; }
    .kpi-card h2 { font-size: 36px; margin: 0; }
    
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
export class DashboardComponent implements OnInit {
  data: DashboardResponse | null = null;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getDashboard().subscribe({
      next: (res) => this.data = res,
      error: (err) => console.error('Erro ao carregar dashboard', err)
    });
  }
}
