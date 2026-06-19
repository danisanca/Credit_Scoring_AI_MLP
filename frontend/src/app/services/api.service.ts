import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Usando rota relativa (Nginx proxy) em produção ou direta no Dev
const API_URL = 'http://localhost:5000/api';

export interface ClienteRequest {
  nome: string;
  idade: number;
  rendaMensal: number;
  tempoEmpregoMeses: number;
  dividaTotal: number;
  qtdEmprestimos: number;
  historicoPagamento: number;
}

export interface ClienteResponse extends ClienteRequest {
  id: string;
  createdAt: string;
}

export interface SolicitarAnaliseRequest {
  clienteId: string;
  valorSolicitado: number;
}

export interface AnaliseResponse {
  id: string;
  clienteId: string;
  nomeCliente: string;
  scoreRisco: number;
  classificacao: string;
  probabilidadeInadimplencia: number;
  valorSolicitado: number;
  aprovado: boolean;
  createdAt: string;
}

export interface DashboardResponse {
  totalAnalises: number;
  totalAprovadas: number;
  totalReprovadas: number;
  taxaAprovacao: number;
  scoreMedio: number;
  ultimasAnalises: AnaliseResponse[];
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  getDashboard(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(`${API_URL}/analises/dashboard`);
  }

  getHistorico(): Observable<AnaliseResponse[]> {
    return this.http.get<AnaliseResponse[]>(`${API_URL}/analises?page=1&pageSize=100`);
  }

  criarCliente(cliente: ClienteRequest): Observable<ClienteResponse> {
    return this.http.post<ClienteResponse>(`${API_URL}/clientes`, cliente);
  }

  solicitarAnalise(request: SolicitarAnaliseRequest): Observable<AnaliseResponse> {
    return this.http.post<AnaliseResponse>(`${API_URL}/analises`, request);
  }

  checkAiHealth(): Observable<any> {
    return this.http.get(`${API_URL}/analises/ai-health`);
  }
}
