import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '@/services/api';
import type { WorkstreamDetail } from '@/types/index';
import {
  AlertTriangle,
  FileText,
  ArrowLeft,
  GitBranch,
  MessageSquare,
  Shield,
  Loader2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const STATUS_BADGE: Record<string, string> = {
  on_track: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  complete: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  at_risk: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  blocked: 'bg-red-500/20 text-red-300 border-red-500/30',
  not_started: 'bg-neutral-600/20 text-neutral-400 border-neutral-500/30',
  in_progress: 'bg-swa-blue/20 text-blue-300 border-swa-blue/30',
  open: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  mitigated: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  needed: 'bg-red-500/20 text-red-300 border-red-500/30',
  pending: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  made: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  deferred: 'bg-neutral-600/20 text-neutral-400 border-neutral-500/30',
};

function Badge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wider border ${STATUS_BADGE[status] || STATUS_BADGE.not_started}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function Section({ title, icon: Icon, count, children, defaultOpen = true }: {
  title: string;
  icon: typeof FileText;
  count?: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-neutral-700/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon size={16} className="text-swa-blue" />
          <span className="text-sm font-semibold text-neutral-200">{title}</span>
          {count !== undefined && (
            <span className="text-xs text-neutral-500 bg-neutral-700 px-2 py-0.5 rounded-full">{count}</span>
          )}
        </div>
        {open ? <ChevronUp size={16} className="text-neutral-400" /> : <ChevronDown size={16} className="text-neutral-400" />}
      </button>
      {open && <div className="px-5 pb-5 border-t border-neutral-700/50">{children}</div>}
    </div>
  );
}

export default function WorkstreamCard() {
  const { id } = useParams<{ id: string }>();
  const [ws, setWs] = useState<WorkstreamDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      try {
        const data = await api.getWorkstream(parseInt(id));
        setWs(data);
      } catch (err) {
        console.error('Failed to load workstream:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin h-10 w-10 text-swa-blue" />
      </div>
    );
  }

  if (!ws) {
    return (
      <div className="text-center py-12">
        <p className="text-neutral-400">Workstream not found</p>
        <Link to="/" className="text-swa-blue hover:underline text-sm mt-2 inline-block">Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link to="/" className="flex items-center gap-1 text-sm text-neutral-500 hover:text-swa-blue transition-colors mb-3">
            <ArrowLeft size={14} /> Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-neutral-100">{ws.name}</h1>
          <p className="text-sm text-neutral-400 mt-1">{ws.purpose}</p>
        </div>
        <Badge status={ws.status} />
      </div>

      {/* Owner + Team */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Owner</p>
          {ws.owner ? (
            <div>
              <p className="text-sm font-medium text-neutral-200">{ws.owner.name}</p>
              {ws.owner.title && <p className="text-xs text-neutral-400">{ws.owner.title}</p>}
            </div>
          ) : (
            <p className="text-sm text-neutral-500">Unassigned</p>
          )}
        </div>
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Team ({ws.members.length})</p>
          <div className="flex flex-wrap gap-2">
            {ws.members.map((m) => (
              <span key={m.id} className="text-xs bg-neutral-700 text-neutral-300 px-2 py-1 rounded-full">
                {m.name} {m.capacity_pct ? `(${m.capacity_pct}%)` : ''}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Scope */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider mb-3">Scope In</p>
          <ul className="space-y-1.5">
            {(ws.scope_in || '').split(',').filter(Boolean).map((item, i) => (
              <li key={i} className="text-sm text-neutral-300 flex items-start gap-2">
                <span className="text-emerald-500 mt-0.5">+</span>
                <span>{item.trim()}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider mb-3">Scope Out</p>
          <ul className="space-y-1.5">
            {(ws.scope_out || '').split(',').filter(Boolean).map((item, i) => (
              <li key={i} className="text-sm text-neutral-300 flex items-start gap-2">
                <span className="text-red-500 mt-0.5">-</span>
                <span>{item.trim()}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Deliverables */}
      <Section title="Deliverables" icon={FileText} count={ws.deliverables.length}>
        <div className="space-y-2 mt-3">
          {ws.deliverables.map((d) => (
            <div key={d.id} className="flex items-center justify-between p-3 bg-neutral-900 rounded-lg">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-neutral-200">{d.name}</p>
                {d.gate && <p className="text-xs text-neutral-500 mt-0.5">Gate: {d.gate.short_name}</p>}
              </div>
              <Badge status={d.status} />
            </div>
          ))}
          {ws.deliverables.length === 0 && <p className="text-sm text-neutral-500 py-2">No deliverables assigned</p>}
        </div>
      </Section>

      {/* Risks */}
      <Section title="Risks" icon={AlertTriangle} count={ws.risks.length}>
        <div className="space-y-2 mt-3">
          {ws.risks.map((r) => (
            <div key={r.id} className="p-3 bg-neutral-900 rounded-lg">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm text-neutral-200">{r.description}</p>
                <Badge status={r.status} />
              </div>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-xs text-neutral-500">Severity: <span className="text-neutral-300">{r.severity}</span></span>
                <span className="text-xs text-neutral-500">Likelihood: <span className="text-neutral-300">{r.likelihood}</span></span>
              </div>
              {r.mitigation && (
                <p className="text-xs text-neutral-400 mt-2 border-t border-neutral-700/50 pt-2">
                  Mitigation: {r.mitigation}
                </p>
              )}
            </div>
          ))}
          {ws.risks.length === 0 && <p className="text-sm text-neutral-500 py-2">No risks identified</p>}
        </div>
      </Section>

      {/* Decisions */}
      <Section title="Decisions Needed" icon={Shield} count={ws.decisions.length} defaultOpen={false}>
        <div className="space-y-2 mt-3">
          {ws.decisions.map((d) => (
            <div key={d.id} className="flex items-center justify-between p-3 bg-neutral-900 rounded-lg">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-neutral-200">{d.description}</p>
                <p className="text-xs text-neutral-500 mt-0.5">
                  Maker: {d.decision_maker} {d.due_date && `| Due: ${d.due_date}`}
                </p>
              </div>
              <Badge status={d.status} />
            </div>
          ))}
        </div>
      </Section>

      {/* Dependencies */}
      <Section title="Dependencies" icon={GitBranch} count={ws.needs_from.length + ws.provides_to.length} defaultOpen={false}>
        <div className="space-y-4 mt-3">
          {ws.needs_from.length > 0 && (
            <div>
              <p className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Needs From</p>
              {ws.needs_from.map((dep) => (
                <div key={dep.id} className="flex items-center justify-between p-3 bg-neutral-900 rounded-lg mb-2">
                  <div>
                    <Link to={`/workstreams/${dep.workstream.id}`} className="text-sm text-swa-blue hover:underline">
                      {dep.workstream.name}
                    </Link>
                    <p className="text-xs text-neutral-400 mt-0.5">{dep.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-neutral-500">{dep.criticality}</span>
                    <Badge status={dep.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
          {ws.provides_to.length > 0 && (
            <div>
              <p className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Provides To</p>
              {ws.provides_to.map((dep) => (
                <div key={dep.id} className="flex items-center justify-between p-3 bg-neutral-900 rounded-lg mb-2">
                  <div>
                    <Link to={`/workstreams/${dep.workstream.id}`} className="text-sm text-swa-blue hover:underline">
                      {dep.workstream.name}
                    </Link>
                    <p className="text-xs text-neutral-400 mt-0.5">{dep.description}</p>
                  </div>
                  <Badge status={dep.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      </Section>

      {/* Status Updates */}
      <Section title="Status Updates" icon={MessageSquare} count={ws.status_updates.length} defaultOpen={false}>
        <div className="space-y-2 mt-3">
          {ws.status_updates.map((su) => (
            <div key={su.id} className="p-3 bg-neutral-900 rounded-lg">
              <div className="flex items-center justify-between mb-1">
                <div className={`w-2 h-2 rounded-full ${
                  su.status_color === 'green' ? 'bg-emerald-500'
                  : su.status_color === 'yellow' ? 'bg-amber-500'
                  : 'bg-red-500'
                }`} />
                <span className="text-xs text-neutral-500">{new Date(su.created_at).toLocaleDateString()}</span>
              </div>
              <p className="text-sm text-neutral-300">{su.content}</p>
            </div>
          ))}
          {ws.status_updates.length === 0 && <p className="text-sm text-neutral-500 py-2">No updates yet</p>}
        </div>
      </Section>
    </div>
  );
}
