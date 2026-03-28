import { useEffect, useState, useRef, useCallback } from 'react';
import { api } from '@/services/api';
import type { DependencyGraphData, CriticalPathData, DependencyNode, DependencyLink } from '@/types/index';
import * as d3 from 'd3';
import { Loader2, Maximize2, ZoomIn, ZoomOut } from 'lucide-react';

const STATUS_COLORS: Record<string, string> = {
  on_track: '#10b981',
  complete: '#3b82f6',
  at_risk: '#f59e0b',
  blocked: '#ef4444',
  not_started: '#6b7280',
  in_progress: '#304CB2',
};

const CRITICALITY_STYLES: Record<string, { stroke: string; width: number; dash: string }> = {
  critical: { stroke: '#ef4444', width: 3, dash: '' },
  high: { stroke: '#f59e0b', width: 2, dash: '' },
  medium: { stroke: '#6b7280', width: 1.5, dash: '6,3' },
  low: { stroke: '#4b5563', width: 1, dash: '4,4' },
};

interface SimNode extends DependencyNode {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface SimLink extends Omit<DependencyLink, 'source' | 'target'> {
  source: SimNode;
  target: SimNode;
}

export default function DependencyGraph() {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<DependencyGraphData | null>(null);
  const [criticalPath, setCriticalPath] = useState<CriticalPathData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState<SimNode | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [graph, cp] = await Promise.all([
          api.getDependencyGraph(),
          api.getCriticalPath(),
        ]);
        setGraphData(graph);
        setCriticalPath(cp);
      } catch (err) {
        console.error('Failed to load dependency graph:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const renderGraph = useCallback(() => {
    if (!graphData || !svgRef.current || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = containerRef.current.clientWidth;
    const height = 560;

    svg.attr('width', width).attr('height', height);

    // Filter links by criticality
    let filteredLinks = [...graphData.links];
    if (selectedFilter !== 'all') {
      filteredLinks = filteredLinks.filter((l) => l.criticality === selectedFilter);
    }

    const nodeMap = new Map<number, SimNode>();
    graphData.nodes.forEach((n) => nodeMap.set(n.id, { ...n }));

    const simNodes: SimNode[] = Array.from(nodeMap.values());
    const simLinks: SimLink[] = filteredLinks
      .filter((l) => nodeMap.has(l.source as unknown as number) && nodeMap.has(l.target as unknown as number))
      .map((l) => ({
        ...l,
        source: nodeMap.get(l.source as unknown as number)!,
        target: nodeMap.get(l.target as unknown as number)!,
      }));

    // Zoom behavior
    const g = svg.append('g');
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Arrow markers
    const defs = svg.append('defs');
    ['critical', 'high', 'medium', 'low'].forEach((crit) => {
      const style = CRITICALITY_STYLES[crit];
      defs.append('marker')
        .attr('id', `arrow-${crit}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 30)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', style.stroke);
    });

    // Force simulation
    const simulation = d3.forceSimulation<SimNode>(simNodes)
      .force('link', d3.forceLink<SimNode, SimLink>(simLinks).id((d) => d.id).distance(180))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50));

    // Links
    const link = g.append('g')
      .selectAll('line')
      .data(simLinks)
      .enter()
      .append('line')
      .attr('stroke', (d) => CRITICALITY_STYLES[d.criticality]?.stroke || '#4b5563')
      .attr('stroke-width', (d) => CRITICALITY_STYLES[d.criticality]?.width || 1)
      .attr('stroke-dasharray', (d) => CRITICALITY_STYLES[d.criticality]?.dash || '')
      .attr('marker-end', (d) => `url(#arrow-${d.criticality})`)
      .attr('opacity', 0.7);

    // Link labels
    const linkLabel = g.append('g')
      .selectAll('text')
      .data(simLinks)
      .enter()
      .append('text')
      .attr('font-size', 9)
      .attr('fill', '#9ca3af')
      .attr('text-anchor', 'middle')
      .text((d) => d.type.replace(/_/g, ' '));

    // Node groups
    const node = g.append('g')
      .selectAll<SVGGElement, SimNode>('g')
      .data(simNodes)
      .enter()
      .append('g')
      .style('cursor', 'grab')
      .on('mouseenter', (_, d) => setHoveredNode(d))
      .on('mouseleave', () => setHoveredNode(null))
      .call(
        d3.drag<SVGGElement, SimNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Node circles
    node.append('circle')
      .attr('r', 22)
      .attr('fill', (d) => STATUS_COLORS[d.status] || STATUS_COLORS.not_started)
      .attr('stroke', '#1f2937')
      .attr('stroke-width', 2)
      .attr('opacity', 0.9);

    // Node labels
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', 9)
      .attr('font-weight', 'bold')
      .attr('fill', '#fff')
      .text((d) => d.short_name);

    // Node name below
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 36)
      .attr('font-size', 10)
      .attr('fill', '#d1d5db')
      .text((d) => d.name.length > 18 ? d.name.substring(0, 16) + '...' : d.name);

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x!)
        .attr('y1', (d) => d.source.y!)
        .attr('x2', (d) => d.target.x!)
        .attr('y2', (d) => d.target.y!);

      linkLabel
        .attr('x', (d) => (d.source.x! + d.target.x!) / 2)
        .attr('y', (d) => (d.source.y! + d.target.y!) / 2 - 6);

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    return () => { simulation.stop(); };
  }, [graphData, selectedFilter]);

  useEffect(() => {
    renderGraph();
  }, [renderGraph]);

  // Resize handler
  useEffect(() => {
    const handleResize = () => renderGraph();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [renderGraph]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin h-10 w-10 text-swa-blue" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs text-neutral-500">Filter:</span>
          {['all', 'critical', 'high', 'medium', 'low'].map((f) => (
            <button
              key={f}
              onClick={() => setSelectedFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                selectedFilter === f
                  ? 'bg-swa-blue text-white'
                  : 'bg-neutral-800 text-neutral-400 hover:bg-neutral-700'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-4 text-xs text-neutral-500">
          <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-red-500 inline-block" /> Critical</span>
          <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-amber-500 inline-block" /> High</span>
          <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-neutral-500 inline-block border-dashed" /> Medium</span>
        </div>
      </div>

      {/* Graph */}
      <div ref={containerRef} className="bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden relative">
        <svg ref={svgRef} className="w-full" style={{ minHeight: 560 }} />

        {/* Hover tooltip */}
        {hoveredNode && (
          <div className="absolute top-4 right-4 bg-neutral-900 border border-neutral-600 rounded-lg p-4 shadow-xl max-w-xs">
            <h4 className="text-sm font-semibold text-neutral-200">{hoveredNode.name}</h4>
            <p className="text-xs text-neutral-400 mt-1">Status: {hoveredNode.status.replace(/_/g, ' ')}</p>
          </div>
        )}

        {/* Zoom controls */}
        <div className="absolute bottom-4 right-4 flex flex-col gap-1">
          <button className="p-2 bg-neutral-700 rounded-lg hover:bg-neutral-600 text-neutral-300" aria-label="Zoom in">
            <ZoomIn size={16} />
          </button>
          <button className="p-2 bg-neutral-700 rounded-lg hover:bg-neutral-600 text-neutral-300" aria-label="Zoom out">
            <ZoomOut size={16} />
          </button>
          <button
            className="p-2 bg-neutral-700 rounded-lg hover:bg-neutral-600 text-neutral-300"
            onClick={renderGraph}
            aria-label="Reset view"
          >
            <Maximize2 size={16} />
          </button>
        </div>
      </div>

      {/* Critical Path Summary */}
      {criticalPath && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wider">Critical Dependencies</p>
            <p className="text-3xl font-bold text-red-400 mt-2">{criticalPath.critical_dependencies}</p>
          </div>
          <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wider">High Dependencies</p>
            <p className="text-3xl font-bold text-amber-400 mt-2">{criticalPath.high_dependencies}</p>
          </div>
          <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wider">Blocked / At Risk</p>
            <p className="text-3xl font-bold text-neutral-100 mt-2">{criticalPath.blocked_or_at_risk.length}</p>
          </div>
        </div>
      )}
    </div>
  );
}
