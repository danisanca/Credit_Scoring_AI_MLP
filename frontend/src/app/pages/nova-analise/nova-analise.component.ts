import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RiskGaugeComponent } from '../../components/risk-gauge/risk-gauge.component';
import { ApiService, AnaliseResponse, ClienteResponse } from '../../services/api.service';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-nova-analise',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, 
    MatButtonModule, MatCardModule, MatProgressSpinnerModule, RiskGaugeComponent
  ],
  template: `
    <div class="analise-page">
      <div class="form-section">
        <h2>Solicitar Análise de Crédito</h2>
        <p class="text-muted">Preencha os dados do cliente para avaliação do modelo MLP PyTorch</p>
        
        <form [formGroup]="form" (ngSubmit)="onSubmit()" class="form-grid mt-4">
          <mat-form-field appearance="outline">
            <mat-label>Nome Completo</mat-label>
            <input matInput formControlName="nome" placeholder="João da Silva">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Idade</mat-label>
            <input matInput type="number" formControlName="idade">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Renda Mensal (R$)</mat-label>
            <input matInput type="number" formControlName="rendaMensal">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Valor Solicitado (R$)</mat-label>
            <input matInput type="number" formControlName="valorSolicitado">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Dívida Atual (R$)</mat-label>
            <input matInput type="number" formControlName="dividaTotal">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Tempo no Emprego Atual (meses)</mat-label>
            <input matInput type="number" formControlName="tempoEmpregoMeses">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Qtd. Empréstimos Anteriores</mat-label>
            <input matInput type="number" formControlName="qtdEmprestimos">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Score Serasa/Histórico (0-100)</mat-label>
            <input matInput type="number" formControlName="historicoPagamento">
          </mat-form-field>

          <div class="full-width">
            <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || loading" class="submit-btn">
              <span *ngIf="!loading">Executar Modelo de IA</span>
              <mat-spinner diameter="24" *ngIf="loading"></mat-spinner>
            </button>
          </div>
        </form>
      </div>

      <div class="result-section" *ngIf="resultado">
        <mat-card class="result-card">
          <mat-card-header>
            <mat-card-title>Resultado da Inferência</mat-card-title>
            <mat-card-subtitle>Analisado em {{ resultado.createdAt | date:'medium' }}</mat-card-subtitle>
          </mat-card-header>
          
          <mat-card-content class="text-center mt-4">
            <app-risk-gauge [score]="resultado.scoreRisco" [classificacao]="resultado.classificacao"></app-risk-gauge>
            
            <div class="decision-box" [ngClass]="resultado.aprovado ? 'approved' : 'denied'">
              <h3>{{ resultado.aprovado ? 'CRÉDITO APROVADO' : 'CRÉDITO NEGADO' }}</h3>
              <p>A rede neural estimou <b>{{ resultado.probabilidadeInadimplencia }}%</b> de chance de inadimplência.</p>
            </div>
            
            <button mat-stroked-button color="primary" (click)="resetForm()" class="mt-4">Nova Consulta</button>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .analise-page { display: flex; gap: 32px; flex-wrap: wrap; }
    .form-section { flex: 1; min-width: 300px; background: var(--bg-secondary); padding: 32px; border-radius: 12px; border: 1px solid var(--bg-tertiary); }
    .result-section { flex: 1; min-width: 300px; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .full-width { grid-column: 1 / -1; }
    .submit-btn { width: 100%; height: 50px; font-size: 16px; font-weight: 600; }
    .mt-4 { margin-top: 24px; }
    .text-center { text-align: center; }
    
    .decision-box { margin-top: 32px; padding: 24px; border-radius: 8px; border: 2px solid transparent; }
    .decision-box.approved { background: rgba(34, 197, 94, 0.1); border-color: var(--success); color: var(--success); }
    .decision-box.denied { background: rgba(239, 68, 68, 0.1); border-color: var(--danger); color: var(--danger); }
    .decision-box h3 { font-size: 20px; font-weight: 800; margin-bottom: 8px; color: inherit; }
    .decision-box p { color: var(--text-primary); margin: 0; }
    
    @media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
  `]
})
export class NovaAnaliseComponent {
  form: FormGroup;
  loading = false;
  resultado: AnaliseResponse | null = null;

  constructor(private fb: FormBuilder, private api: ApiService) {
    this.form = this.fb.group({
      nome: ['', Validators.required],
      idade: [35, [Validators.required, Validators.min(18)]],
      rendaMensal: [5000, Validators.required],
      valorSolicitado: [20000, Validators.required],
      dividaTotal: [15000, Validators.required],
      tempoEmpregoMeses: [36, Validators.required],
      qtdEmprestimos: [2, Validators.required],
      historicoPagamento: [75, [Validators.required, Validators.min(0), Validators.max(100)]],
    });
  }

  onSubmit() {
    if (this.form.invalid) return;
    this.loading = true;
    this.resultado = null;

    const data = this.form.value;
    
    // 1. Cria o cliente
    // 2. Solicita a análise para o cliente criado
    this.api.criarCliente({
      nome: data.nome,
      idade: data.idade,
      rendaMensal: data.rendaMensal,
      tempoEmpregoMeses: data.tempoEmpregoMeses,
      dividaTotal: data.dividaTotal,
      qtdEmprestimos: data.qtdEmprestimos,
      historicoPagamento: data.historicoPagamento
    }).pipe(
      switchMap((cliente: ClienteResponse) => {
        return this.api.solicitarAnalise({
          clienteId: cliente.id,
          valorSolicitado: data.valorSolicitado
        });
      })
    ).subscribe({
      next: (res) => {
        this.resultado = res;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erro na análise', err);
        alert('Erro ao processar análise. Verifique os logs.');
        this.loading = false;
      }
    });
  }

  resetForm() {
    this.resultado = null;
    this.form.reset({
      idade: 35, rendaMensal: 5000, valorSolicitado: 20000, dividaTotal: 15000,
      tempoEmpregoMeses: 36, qtdEmprestimos: 2, historicoPagamento: 75
    });
  }
}
