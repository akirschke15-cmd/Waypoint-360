import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/services/api';
import type { Program, WorkstreamSummary, Gate, CriticalPathData, AIQueryResponse } from '@/types/index';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Send,
  Shield,
  GitBranch,
  BarChart3,
  ChevronRight,
  Loader2,
} from 'lucide-react';

const STATUS_STYLES: Record<string, string> = {
  on_track: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  complete: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  at_risk: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  blocked: 'bg-red-500/20 text-red-300 border-red-500/30',
  not_started: 'bg-neutral-600/20 text-neutral-400 border-neutral-500/30',
  in_progress: 'bg-swa-blue/20 text-blue-300 border-swa-blue/30',
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${STATUS_STYLES[status] || STATUS_STYLES.not_started}`}>
      {status === 'on_track' && <CheckCircle size={12} />}
      {status === 'at_risk' && <AlertTriangle size={12} />}
      {status === 'blocked' && <Shield size={12} />}
      {status === 'in_progress' && <Zap size={12} />}
      {status.replace(/_/g, ' ').toUpperCase()}
    </span>
  );
}

function KPICard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon: typeof BarChart3; color: string }) {
  return (
    <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-neutral-400">{label}</p>
        <Icon size={20} className={color} />
      </div>
      <p className="text-3xl font-bold text-neutral-100">{value}</p>
    </div>
  );
}

export default function CommandCenter() {
  const [program, setProgram] = useState<Program | null>(null);
  const [workstreams, setWorkstreams] = useState<WorkstreamSummary[]>([]);
  const [gates, setGates] = useState<Gate[]>([]);
  const [criticalPath, setCriticalPath] = useState<CriticalPathData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AI chat
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<AIQueryResponse[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [prog, ws, g, cp] = await Promise.all([
          api.getProgram(),
          api.getWorkstreams(),
          api.getGates(),
          api.getCriticalPath(),
        ]);
        setProgram(prog);
        setWorkstreams(ws);
        setGates(g);
        setCriticalPath(cp);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleChat = async () => {
    if (!chatInput.trim()) return;
    setChatLoading(true);
    try {
      const response = await api.aiQuery(chatInput.trim());
      setChatHistory((prev) => [...prev, response]);
      setChatInput('');
    } catch {
      setChatHistory((prev) => [
        ...prev,
        {
          query: chatInput,
          intent: 'error',
          response: 'Failed to process query. LangGraph integration pending.',
          recommendations: [],
          sources: [],
          confidence: 0,
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="animate-spin h-10 w-10 text-swa-blue mx-auto mb-4" />
          <p className="text-neutral-400 text-sm">Loading Waypoint 360...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-red-400 mb-2">Connection Error</h3>
        <p className="text-neutral-300 text-sm">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-swa-blue text-white rounded-lg text-sm hover:bg-swa-blue/80 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  const onTrack = workstreams.filter((w) => w.status === 'on_track').length;
  const atRisk = workstreams.filter((w) => w.status === 'at_risk').length;
  const blocked = workstreams.filter((w) => w.status === 'blocked').length;
  const currentGate = gates.find((g) => g.status === 'in_progress');
  const totalDeliverables = workstreams.reduce((sum, w) => sum + w.deliverable_count, 0);
  const completedDeliverables = workstreams.reduce((sum, w) => sum + w.deliverables_complete, 0);
  const openRisks = workstreams.reduce((sum, w) => sum + w.risk_count, 0);

  return (
    <div className="space-y-6">
      {/* Program Banner */}
      {program && (
        <div className="bg-gradient-to-r from-swa-blue/20 via-neutral-800 to-neutral-800 border border-swa-blue/30 rounded-xl p-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-neutral-100">{program.name}</h1>
              <p className="text-sm text-neutral-400 mt-1 max-w-2xl">{program.description}</p>
            </div>
            <StatusBadge status={program.status} />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5 pt-5 border-t border-neutral-700/50">
            <div>
              <p className="text-xs text-neutral-500 uppercase tracking-wider">Current Gate</p>
              <p className="text-lg font-bold text-swa-blue mt-1">{currentGate?.short_name || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 uppercase tracking-wider">Workstreams</p>
              <p className="text-lg font-bold text-neutral-100 mt-1">{workstreams.length}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 uppercase tracking-wider">Phases</p>
              <p className="text-lg font-bold text-neutral-100 mt-1">{program.phases.length}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 uppercase tracking-wider">Gates</p>
              <p className="text-lg font-bold text-neutral-100 mt-1">{gates.length}</p>
            </div>
          </div>
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard label="On Track" value={onTrack} icon={CheckCircle} color="text-emerald-400" />
        <KPICard label="At Risk" value={atRisk} icon={AlertTriangle} color="text-amber-400" />
        <KPICard label="Blocked" value={blocked} icon={Shield} color="text-red-400" />
        <KPICard label="Open Risks" value={openRisks} icon={AlertTriangle} color="text-swa-gold" />
        <KPICard
          label="Deliverables"
          value={`${completedDeliverables}/${totalDeliverables}`}
          icon={BarChart3}
          color="text-swa-blue"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workstream Status Panel */}
        <div className="lg:col-span-1 bg-neutral-800 border border-neutral-700 rounded-xl">
          <div className="px-5 py-4 border-b border-neutral-700 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-neutral-200">Workstreams</h3>
            <span className="text-xs text-neutral-500">{workstreams.length} total</span>
          </div>
          <div className="divide-y divide-neutral-700/50 max-h-[480px] overflow-y-auto">
            {workstreams.map((ws) => (
              <Link
                key={ws.id}
                to={`/workstreams/${ws.id}`}
                className="flex items-center justify-between px-5 py-3 hover:bg-neutral-700/30 transition-colors group"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-neutral-200 group-hover:text-swa-blue transition-colors truncate">
                    {ws.short_name}
                  </p>
                  <p className="text-xs text-neutral-500 truncate">{ws.owner?.name || 'Unassigned'}</p>
                </div>
                <div className="flex items-center gap-2 ml-3">
                  <StatusBadge status={ws.status} />
                  <ChevronRight size={14} className="text-neutral-600 group-hover:text-neutral-400" />
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* AI Chat + Gate Progress */}
        <div className="lg:col-span-2 space-y-6">
          {/* AI Command Interface */}
          <div className="bg-neutral-800 border border-neutral-700 rounded-xl">
            <div className="px-5 py-4 border-b border-neutral-700 flex items-center gap-2">
              <Zap size={16} className="text-swa-gold" />
              <h3 className="text-sm font-semibold text-neutral-200">AI Analysis</h3>
              <span className="text-xs text-neutral-500 ml-auto">LangGraph powered</span>
            </div>
            <div className="p-5">
              {/* Chat history */}
              <div className="space-y-4 mb-4 max-h-48 overflow-y-auto">
                {chatHistory.length === 0 && (
                  <div className="text-center py-6">
                    <Zap size={24} className="text-neutral-600 mx-auto mb-2" />
                    <p className="text-sm text-neutral-500">
                      Ask about gate readiness, scope creep, risks, or program status
                    </p>
                  </div>
                )}
                {chatHistory.map((msg, i) => (
                  <div key={i} className="space-y-2">
                    <div className="flex justify-end">
                      <div className="bg-swa-blue/20 border border-swa-blue/30 rounded-lg px-3 py-2 max-w-xs">
                        <p className="text-sm text-neutral-200">{msg.query}</p>
                      </div>
                    </div>
                    <div className="flex justify-start">
                      <div className="bg-neutral-700/50 border border-neutral-600 rounded-lg px-3 py-2 max-w-md">
                        <p className="text-sm text-neutral-300">{msg.response}</p>
                        {msg.confidence > 0 && (
                          <p className="text-xs text-neutral-500 mt-1">Confidence: {(msg.confidence * 100).toFixed(0)}%</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {/* Input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Ask about program status, risks, dependencies..."
                  className="flex-1 bg-neutral-900 border border-neutral-600 rounded-lg px-4 py-2.5 text-sm text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-swa-blue transition-colors"
                />
                <button
                  onClick={handleChat}
                  disabled={chatLoading || !chatInput.trim()}
                  className="px-4 py-2.5 bg-swa-blue text-white rounded-lg hover:bg-swa-blue/80 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {chatLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </div>
            </div>
          </div>

          {/* Gate Progress */}
          <div className="bg-neutral-800 border border-neutral-700 rounded-xl">
            <div className="px-5 py-4 border-b border-neutral-700 flex items-center gap-2">
              <Clock size={16} className="text-swa-blue" />
              <h3 className="text-sm font-semibold text-neutral-200">Gate Progress</h3>
              <Link to="/gates" className="text-xs text-swa-blue hover:underline ml-auto">View Timeline</Link>
            </div>
            <div className="p-5 space-y-3">
              {gates.map((gate) => {
                const pct = gate.criteria_total > 0
                  ? Math.round((gate.criteria_complete / gate.criteria_total) * 100)
                  : 0;
                return (
                  <div key={gate.id} className="flex items-center gap-4">
                    <div className="w-20 text-xs font-medium text-neutral-400">{gate.short_name}</div>
                    <div className="flex-1 bg-neutral-700 rounded-full h-2.5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          gate.status === 'complete'
                            ? 'bg-emerald-500'
                            : gate.status === 'in_progress'
                            ? 'bg-swa-blue'
                            : 'bg-neutral-600'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="w-20 text-right">
                      <span className="text-xs text-neutral-400">
                        {gate.criteria_complete}/{gate.criteria_total}
                      </span>
                    </div>
                    <StatusBadge status={gate.status || 'not_started'} />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Critical Dependencies */}
          {criticalPath && (
            <div className="bg-neutral-800 border border-neutral-700 rounded-xl">
              <div className="px-5 py-4 border-b border-neutral-700 flex items-center gap-2">
                <GitBranch size={16} className="text-swa-red" />
                <h3 className="text-sm font-semibold text-neutral-200">Critical Dependencies</h3>
                <Link to="/dependencies" className="text-xs text-swa-blue hover:underline ml-auto">View Graph</Link>
              </div>
              <div className="p-5">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-neutral-900 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-swa-red">{criticalPath.critical_dependencies}</p>
                    <p className="text-xs text-neutral-500">Critical</p>
                  </div>
                  <div className="bg-neutral-900 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-amber-400">{criticalPath.high_dependencies}</p>
                    <p className="text-xs text-neutral-500">High</p>
                  </div>
                </div>
                {criticalPath.blocked_or_at_risk.length > 0 ? (
                  <div className="space-y-2">
                    {criticalPath.blocked_or_at_risk.map((item) => (
                      <div key={item.dependency_id} className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                        <p className="text-sm text-neutral-200">
                          {item.from.name} → {item.to.name}
                        </p>
                        <p className="text-xs text-neutral-400 mt-1">{item.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-neutral-500 text-center py-2">No blocked dependencies</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
