// Types matching actual backend API responses

export interface Person {
  id: number;
  name: string;
  title?: string;
  capacity_pct?: number;
}

export interface GateExitCriteria {
  id: number;
  description: string;
  status: string;
  notes?: string;
}

export interface Phase {
  id: number;
  name: string;
  description: string;
  start_week: number;
  end_week: number | null;
  goal: string;
}

export interface GateSummary {
  id: number;
  name: string;
  short_name: string;
  week_number: number;
  status: string;
  exit_criteria: GateExitCriteria[];
}

export interface Gate {
  id: number;
  name: string;
  short_name: string;
  description: string;
  week_number: number;
  due_date: string | null;
  status: string;
  exit_criteria: GateExitCriteria[];
  criteria_complete: number;
  criteria_total: number;
}

export interface GateDetail extends Gate {
  workstream_deliverables: Array<{
    workstream: { id: number; name: string };
    deliverables: Array<{
      id: number;
      name: string;
      status: string;
    }>;
  }>;
}

export interface WorkstreamSummary {
  id: number;
  name: string;
  short_name: string;
  purpose: string;
  status: string;
  owner: Person | null;
  risk_count: number;
  deliverable_count: number;
  deliverables_complete: number;
}

export interface Deliverable {
  id: number;
  name: string;
  description: string;
  status: string;
  gate: { id: number; name: string; short_name: string } | null;
}

export interface Risk {
  id: number;
  description: string;
  severity: string;
  likelihood: string;
  mitigation: string;
  status: string;
}

export interface Decision {
  id: number;
  description: string;
  status: string;
  decision_maker: string;
  due_date: string | null;
}

export interface DependencyRef {
  id: number;
  workstream: { id: number; name: string };
  description: string;
  status: string;
  criticality: string;
}

export interface StatusUpdate {
  id: number;
  content: string;
  status_color: string;
  created_at: string;
}

export interface WorkstreamDetail {
  id: number;
  name: string;
  short_name: string;
  purpose: string;
  scope_in: string | null;
  scope_out: string | null;
  baseline_scope: string | null;
  status: string;
  owner: Person | null;
  members: Person[];
  deliverables: Deliverable[];
  risks: Risk[];
  decisions: Decision[];
  needs_from: DependencyRef[];
  provides_to: DependencyRef[];
  status_updates: StatusUpdate[];
}

export interface Program {
  id: number;
  name: string;
  description: string;
  status: string;
  phases: Phase[];
  gates: GateSummary[];
  workstreams: WorkstreamSummary[];
}

// Dependency graph types (D3 format)
export interface DependencyNode {
  id: number;
  name: string;
  short_name: string;
  status: string;
  group: number;
}

export interface DependencyLink {
  id: number;
  source: number;
  target: number;
  description: string;
  type: string;
  status: string;
  criticality: string;
  gate: string | null;
}

export interface DependencyGraphData {
  nodes: DependencyNode[];
  links: DependencyLink[];
}

export interface CriticalPathData {
  critical_dependencies: number;
  high_dependencies: number;
  blocked_or_at_risk: Array<{
    dependency_id: number;
    from: { id: number; name: string };
    to: { id: number; name: string };
    description: string;
    status: string;
    criticality: string;
  }>;
}

// Gate timeline matrix types
export interface TimelineGate {
  id: number;
  name: string;
  short_name: string;
  week: number;
}

export interface TimelineCell {
  gate_id: number;
  status: string;
  deliverable_count: number;
}

export interface TimelineRow {
  workstream: { id: number; name: string; short_name: string };
  gates: Record<string, TimelineCell>;
}

export interface GateTimelineData {
  gates: TimelineGate[];
  matrix: TimelineRow[];
}

// AI endpoint response types
export interface AIQueryResponse {
  query: string;
  intent: string;
  response: string;
  recommendations: string[];
  sources: string[];
  confidence: number;
}

export interface GateReadinessResponse {
  gate_id: number;
  status: string;
  message: string;
  confidence: number;
  workstream_readiness: unknown[];
  blockers: string[];
  recommendations: string[];
}

export interface ScopeCreepResponse {
  status: string;
  message: string;
  workstreams_flagged: unknown[];
  total_changes: number;
}

export interface ExecutiveSummaryResponse {
  status: string;
  message: string;
  summary: string;
  key_highlights: string[];
  action_items: string[];
}
