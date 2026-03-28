import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/services/api';
import type { GateTimelineData, Gate } from '@/types/index';
import { Clock, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';

const CELL_COLORS: Record<string, string> = {
  complete: 'bg-emerald-500/30 border-emerald-500/40 text-emerald-300',
  in_progress: 'bg-swa-blue/30 border-swa-blue/40 text-blue-300',
  at_risk: 'bg-amber-500/30 border-amber-500/40 text-amber-300',
  blocked: 'bg-red-500/30 border-red-500/40 text-red-300',
  not_started: 'bg-neutral-700/30 border-neutral-600/40 text-neutral-500',
};

export default function GateTimeline() {
  const [timeline, setTimeline] = useState<GateTimelineData | null>(null);
  const [gates, setGates] = useState<Gate[]>([]);
  const [expandedGate, setExpandedGate] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [timelineData, gatesData] = await Promise.all([
          api.getGateTimeline(),
          api.getGates(),
        ]);
        setTimeline(timelineData);
        setGates(gatesData);
      } catch (err) {
        console.error('Failed to load timeline:', err);
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

  if (!timeline) return null;

  return (
    <div className="space-y-6">
      {/* Timeline Matrix */}
      <div className="bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-neutral-700">
          <h3 className="text-sm font-semibold text-neutral-200">Workstream x Gate Matrix</h3>
          <p className="text-xs text-neutral-500 mt-1">Deliverable status by workstream across all gates</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-700">
                <th className="text-left text-xs font-medium text-neutral-400 px-4 py-3 sticky left-0 bg-neutral-800 min-w-[160px]">
                  Workstream
                </th>
                {timeline.gates.map((g) => (
                  <th key={g.id} className="text-center text-xs font-medium text-neutral-400 px-3 py-3 min-w-[100px]">
                    <div>{g.short_name}</div>
                    <div className="text-neutral-600 font-normal">Wk {g.week}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-700/50">
              {timeline.matrix.map((row) => (
                <tr key={row.workstream.id} className="hover:bg-neutral-700/20 transition-colors">
                  <td className="px-4 py-3 sticky left-0 bg-neutral-800">
                    <Link
                      to={`/workstreams/${row.workstream.id}`}
                      className="text-sm font-medium text-neutral-200 hover:text-swa-blue transition-colors"
                    >
                      {row.workstream.short_name}
                    </Link>
                  </td>
                  {timeline.gates.map((g) => {
                    const cell = row.gates[g.short_name];
                    if (!cell) return <td key={g.id} className="px-3 py-3" />;
                    return (
                      <td key={g.id} className="px-3 py-3">
                        <div
                          className={`rounded-lg border px-2 py-1.5 text-center text-xs font-medium ${CELL_COLORS[cell.status] || CELL_COLORS.not_started}`}
                        >
                          {cell.deliverable_count > 0 ? (
                            <>
                              <div className="text-[10px] uppercase tracking-wider">{cell.status.replace(/_/g, ' ')}</div>
                              <div className="text-[10px] opacity-60 mt-0.5">{cell.deliverable_count} items</div>
                            </>
                          ) : (
                            <div className="text-[10px]">--</div>
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

      {/* Gate Details */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-neutral-200 px-1">Gate Exit Criteria</h3>
        {gates.map((gate) => {
          const isExpanded = expandedGate === gate.id;
          const pct = gate.criteria_total > 0
            ? Math.round((gate.criteria_complete / gate.criteria_total) * 100)
            : 0;

          return (
            <div key={gate.id} className="bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden">
              <button
                onClick={() => setExpandedGate(isExpanded ? null : gate.id)}
                className="w-full flex items-center justify-between px-5 py-4 hover:bg-neutral-700/30 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <Clock size={16} className="text-swa-blue" />
                  <span className="text-sm font-semibold text-neutral-200">{gate.short_name}</span>
                  <span className="text-xs text-neutral-500 hidden sm:inline">{gate.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="hidden sm:flex items-center gap-2">
                    <div className="w-24 bg-neutral-700 rounded-full h-2 overflow-hidden">
                      <div className="h-full bg-swa-blue rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-xs text-neutral-400 w-12 text-right">{pct}%</span>
                  </div>
                  <span className="text-xs text-neutral-500">Wk {gate.week_number}</span>
                  {isExpanded ? <ChevronUp size={16} className="text-neutral-400" /> : <ChevronDown size={16} className="text-neutral-400" />}
                </div>
              </button>
              {isExpanded && (
                <div className="px-5 pb-4 border-t border-neutral-700/50">
                  <p className="text-xs text-neutral-400 py-3">{gate.description}</p>
                  <div className="space-y-2">
                    {gate.exit_criteria.map((ec) => (
                      <div key={ec.id} className="flex items-start gap-3 p-3 bg-neutral-900 rounded-lg">
                        <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                          ec.status === 'complete' ? 'bg-emerald-500'
                          : ec.status === 'in_progress' ? 'bg-swa-blue'
                          : ec.status === 'at_risk' ? 'bg-amber-500'
                          : 'bg-neutral-600'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-neutral-300">{ec.description}</p>
                          {ec.notes && <p className="text-xs text-neutral-500 mt-1">{ec.notes}</p>}
                        </div>
                        <span className="text-xs text-neutral-500 flex-shrink-0">{ec.status.replace(/_/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
