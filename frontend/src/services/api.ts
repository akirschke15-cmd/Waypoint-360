import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Program,
  WorkstreamSummary,
  WorkstreamDetail,
  Gate,
  GateDetail,
  GateTimelineData,
  DependencyGraphData,
  CriticalPathData,
  AIQueryResponse,
  GateReadinessResponse,
  ScopeCreepResponse,
  ExecutiveSummaryResponse,
} from '@/types/index';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    name: string;
    email: string;
    role: string;
    title?: string;
    organization?: string;
  };
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    });

    // Attach JWT token to all requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response.data,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/';
        }
        const message = error.response?.data
          ? JSON.stringify(error.response.data)
          : error.message;
        console.error(`API ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);
        return Promise.reject(error);
      }
    );
  }

  // Auth
  login(email: string, password: string): Promise<LoginResponse> {
    return this.client.post('/auth/login', { email, password });
  }

  getMe(): Promise<LoginResponse['user']> {
    return this.client.get('/auth/me');
  }

  // Program
  getProgram(): Promise<Program> {
    return this.client.get('/program/');
  }

  seedDatabase(): Promise<{ status: string; message: string }> {
    return this.client.post('/program/seed');
  }

  // Workstreams
  getWorkstreams(): Promise<WorkstreamSummary[]> {
    return this.client.get('/workstreams/');
  }

  getWorkstream(id: number): Promise<WorkstreamDetail> {
    return this.client.get(`/workstreams/${id}`);
  }

  createWorkstream(data: Record<string, unknown>): Promise<{ status: string; id: number }> {
    return this.client.post('/workstreams/', data);
  }

  updateWorkstream(id: number, data: Partial<WorkstreamDetail>): Promise<{ status: string; id: number }> {
    return this.client.put(`/workstreams/${id}`, data);
  }

  // Gates
  getGates(): Promise<Gate[]> {
    return this.client.get('/gates/');
  }

  getGate(id: number): Promise<GateDetail> {
    return this.client.get(`/gates/${id}`);
  }

  getGateTimeline(): Promise<GateTimelineData> {
    return this.client.get('/gates/timeline');
  }

  updateGateCriteria(gateId: number, criteriaId: number, data: Record<string, unknown>): Promise<unknown> {
    return this.client.put(`/gates/${gateId}/criteria/${criteriaId}`, data);
  }

  // Dependencies
  getDependencyGraph(): Promise<DependencyGraphData> {
    return this.client.get('/dependencies/');
  }

  getCriticalPath(): Promise<CriticalPathData> {
    return this.client.get('/dependencies/critical-path');
  }

  createDependency(data: Record<string, unknown>): Promise<unknown> {
    return this.client.post('/dependencies/', data);
  }

  // Risks
  getRisks(params?: Record<string, unknown>): Promise<unknown[]> {
    return this.client.get('/risks/', { params });
  }

  createRisk(data: Record<string, unknown>): Promise<unknown> {
    return this.client.post('/risks/', data);
  }

  updateRisk(id: number, data: Record<string, unknown>): Promise<unknown> {
    return this.client.put(`/risks/${id}`, data);
  }

  deleteRisk(id: number): Promise<unknown> {
    return this.client.delete(`/risks/${id}`);
  }

  // Decisions
  getDecisions(params?: Record<string, unknown>): Promise<unknown[]> {
    return this.client.get('/decisions/', { params });
  }

  createDecision(data: Record<string, unknown>): Promise<unknown> {
    return this.client.post('/decisions/', data);
  }

  updateDecision(id: number, data: Record<string, unknown>): Promise<unknown> {
    return this.client.put(`/decisions/${id}`, data);
  }

  // Deliverables
  getDeliverables(params?: Record<string, unknown>): Promise<unknown[]> {
    return this.client.get('/deliverables/', { params });
  }

  createDeliverable(data: Record<string, unknown>): Promise<unknown> {
    return this.client.post('/deliverables/', data);
  }

  updateDeliverable(id: number, data: Record<string, unknown>): Promise<unknown> {
    return this.client.put(`/deliverables/${id}`, data);
  }

  // Status Updates
  getStatusUpdates(params?: Record<string, unknown>): Promise<unknown[]> {
    return this.client.get('/status-updates/', { params });
  }

  createStatusUpdate(data: Record<string, unknown>): Promise<unknown> {
    return this.client.post('/status-updates/', data);
  }

  // Scope Changes
  getScopeChanges(params?: Record<string, unknown>): Promise<unknown[]> {
    return this.client.get('/scope-changes/', { params });
  }

  createScopeChange(data: Record<string, unknown>): Promise<unknown> {
    return this.client.post('/scope-changes/', data);
  }

  // AI endpoints
  aiQuery(query: string): Promise<AIQueryResponse> {
    return this.client.post('/ai/query', { query });
  }

  getGateReadiness(gateId: number): Promise<GateReadinessResponse> {
    return this.client.get(`/ai/gate-readiness/${gateId}`);
  }

  getScopeCreep(): Promise<ScopeCreepResponse> {
    return this.client.get('/ai/scope-creep');
  }

  getExecutiveSummary(): Promise<ExecutiveSummaryResponse> {
    return this.client.get('/ai/summary');
  }
}

export const api = new ApiService();
