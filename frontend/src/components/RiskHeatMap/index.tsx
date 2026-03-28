import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/services/api';
import type { WorkstreamSummary, WorkstreamDetail, Risk } from '@/types/index';
import { AlertTriangle, Loader2 } from 'lucide-react';

interface RiskWithWorkstream extends Risk {
  workstream_id: number;
  workstream_name: string;
}

const SEVERITY_ORDER = ['critical', 'high', 'medium', 'low'];
const LIKELIHOOD_ORDER = ['very_high', 'high', 'medium', 'low', 'very_low'];
const SEVERITY_LABEL: Record<string, string> = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' };
const LIKELIHOOD_LABEL: Record<string, string> = { very_high: 'Very High', high: 'High', medium: 'Medium', low: 'Low', very_low: 'Very Low' };

const CELL_BG: Record<string, string> = {
  // severity-likelihood combos for heatmap coloring
  'critical-very_high': 'bg-red-600/40',
  'critical-high': 'bg-red-500/35',
  'critical-medium': 'bg-red-500/25',
  'critical-low': 'bg-amber-500/25',
  'critical-very_low': 'bg-amber-500/15',
  'high-very_high': 'bg-red-500/35',
  'high-high': 'bg-red-500/25',
  'high-medium': 'bg-amber-500/25',
  'high-low': 'bg-amber-500/15',
  'high-very_low': 'bg-neutral-700/30',
  'medium-very_high': 'bg-amber-500/25',
  'medium-high': 'bg-amber-500/15',
  'medium-medium': 'bg-neutral-700/30',
  'medium-low': 'bg-neutral-700/20',
  'medium-very_low': 'bg-neutral-700/10',
  'low-very_high': 'bg-amber-500/15',
  'low-high': 'bg-neutral-700/30',
  'low-medium': 'bg-neutral-700/20',
  'low-low': 'bg-neutral-700/10',
  'low-very_low': 'bg-neutral-800/50',
};

export default function RiskHeatMap() {
  const [risks, setRisks] = useState<RiskWithWorkstream[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const workstreams: WorkstreamSummary[] = await api.getWorkstreams();
        const detailPromises = workstreams.map((ws) => api.getWorkstream(ws.id));
        const details: WorkstreamDetail[] = await Promise.all(detailPromises);

        const allRisks: RiskWithWorkstream[] = [];
        details.forEach((ws) => {
          ws.risks.forEach((r) => {
            allRisks.push({ ...r, workstream_id: ws.id, workstream_name: ws.short_name });
          });
        });
        setRisks(allRisks);
      } catch (err) {
        console.error('Failed to load risks:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin h-10 w-10 text-swa-blue" />
      </div>
    );
  }

  const filteredRisks = filter === 'all' ? risks : risks.filter((r) => r.status === filter);
  const openRisks = risks.filter((r) => r.status === 'open');
  const criticalRisks = risks.filter((r) => r.severity === 'critical' || r.severity === 'high');

  // Build heatmap data
  const heatmapData: Record<string, RiskWithWorkstream[]> = {};
  filteredRisks.forEach((r) => {
    const key = `${r.severity}-${r.likelihood}`;
    if (!heatmapData[key]) heatmapData[key] = [];
    heatmapData[key].push(r);
  });

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider">Total Risks</p>
          <p className="text-3xl font-bold text-neutral-100 mt-2">{risks.length}</p>
        </div>
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider">Open Risks</p>
          <p className="text-3xl font-bold text-amber-400 mt-2">{openRisks.length}</p>
        </div>
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wider">Critical / High</p>
          <p className="text-3xl font-bold text-red-400 mt-2">{criticalRisks.length}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-neutral-500">Status:</span>
        {['all', 'open', 'mitigated', 'closed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filter === f ? 'bg-swa-blue text-white' : 'bg-neutral-800 text-neutral-400 hover:bg-neutral-700'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Heatmap */}
      <div className="bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-neutral-700">
          <h3 className="text-sm font-semibold text-neutral-200">Severity x Likelihood Matrix</h3>
        </div>
        <div className="p-5 overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="text-xs text-neutral-500 text-left px-2 py-2 w-24">Severity \ Likelihood</th>
                {LIKELIHOOD_ORDER.map((l) => (
                  <th key={l} className="text-xs text-neutral-400 text-center px-2 py-2 min-w-[100px]">
                    {LIKELIHOOD_LABEL[l] || l}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SEVERITY_ORDER.map((s) => (
                <tr key={s}>
                  <td className="text-xs text-neutral-400 font-medium px-2 py-2">{SEVERITY_LABEL[s] || s}</td>
                  {LIKELIHOOD_ORDER.map((l) => {
                    const key = `${s}-${l}`;
                    const cellRisks = heatmapData[key] || [];
                    return (
                      <td key={l} className="px-1 py-1">
                        <div className={`rounded-lg border border-neutral-600/30 min-h-[60px] p-2 ${CELL_BG[key] || 'bg-neutral-800/50'}`}>
                          {cellRisks.length > 0 ? (
                            <div className="space-y-1">
                              {cellRisks.map((r) => (
                                <div key={r.id} className="text-[10px] text-neutral-300 flex items-center gap-1">
                                  <AlertTriangle size={10} className="text-amber-400 flex-shrink-0" />
                                  <span className="truncate">{r.workstream_name}</span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <span className="text-[10px] text-neutral-600">--</span>
                          )}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Risk List */}
      <div className="bg-neutral-800 border border-neutral-700 rounded-xl">
        <div className="px-5 py-4 border-b border-neutral-700">
          <h3 className="text-sm font-semibold text-neutral-200">Risk Register ({filteredRisks.length})</h3>
        </div>
        <div className="divide-y divide-neutral-700/50 max-h-[400px] overflow-y-auto">
          {filteredRisks.map((r) => (
            <div key={r.id} className="px-5 py-3 hover:bg-neutral-700/20 transition-colors">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-sm text-neutral-200">{r.description}</p>
                  <div className="flex items-center gap-3 mt-1.5">
                    <Link to={`/workstreams/${r.workstream_id}`} className="text-xs text-swa-blue hover:underline">
                      {r.workstream_name}
                    </Link>
                    <span className="text-xs text-neutral-500">Sev: {r.severity}</span>
                    <span className="text-xs text-neutral-500">Lkl: {r.likelihood}</span>
                  </div>
                  {r.mitigation && <p className="text-xs text-neutral-400 mt-1.5">Mitigation: {r.mitigation}</p>}
                </div>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium uppercase border ${
                  r.status === 'open' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                  : r.status === 'mitigated' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                  : 'bg-neutral-600/20 text-neutral-400 border-neutral-500/30'
                }`}>
                  {r.status}
                </span>
              </div>
            </div>
          ))}
          {filteredRisks.length === 0 && (
            <div className="px-5 py-8 text-center text-sm text-neutral-500">No risks match this filter</div>
          )}
        </div>
      </div>
    </div>
  );
}
