import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { 
    path: 'dashboard', 
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent) 
  },
  { 
    path: 'nova-analise', 
    loadComponent: () => import('./pages/nova-analise/nova-analise.component').then(m => m.NovaAnaliseComponent) 
  },
  { 
    path: 'historico', 
    loadComponent: () => import('./pages/historico/historico.component').then(m => m.HistoricoComponent) 
  }
];
