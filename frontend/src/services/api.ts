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

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    });

    this.client.interceptors.response.use(
      (response) => response.data,
      (error: AxiosError) => {
        const message = error.response?.data
          ? JSON.stringify(error.response.data)
          : error.message;
        console.error(`API ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);
        return Promise.reject(error);
      }
    );
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

  // Dependencies
  getDependencyGraph(): Promise<DependencyGraphData> {
    return this.client.get('/dependencies/');
  }

  getCriticalPath(): Promise<CriticalPathData> {
    return this.client.get('/dependencies/critical-path');
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
