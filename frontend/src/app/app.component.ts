import { Component } from '@angular/core';
import { RouterOutlet, RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterModule, MatToolbarModule, MatButtonModule, MatIconModule],
  template: `
    <mat-toolbar color="primary" class="toolbar">
      <div class="logo">
        <mat-icon>analytics</mat-icon>
        <span>CreditAI</span>
      </div>
      <div class="nav-links">
        <a mat-button routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
        <a mat-button routerLink="/nova-analise" routerLinkActive="active">Nova Análise</a>
        <a mat-button routerLink="/historico" routerLinkActive="active">Histórico</a>
      </div>
    </mat-toolbar>

    <main class="container">
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    .toolbar {
      display: flex;
      justify-content: space-between;
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--bg-tertiary);
      color: var(--text-primary);
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      font-size: 1.2rem;
    }
    .nav-links a {
      color: var(--text-secondary);
      margin-left: 8px;
    }
    .nav-links a.active {
      color: var(--accent);
      background: rgba(107, 76, 255, 0.1);
    }
    .container {
      padding: 32px;
      max-width: 1200px;
      margin: 0 auto;
    }
  `]
})
export class AppComponent {}
