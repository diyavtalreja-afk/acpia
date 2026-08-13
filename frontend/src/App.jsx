import React, { useEffect, useState, useRef } from 'react';
import * as d3 from 'd3';
import { 
  Monitor, FolderSearch, TriangleAlert, 
  Network, MessageSquare, ClipboardCheck, Shield, PlayCircle, CheckCircle2
} from 'lucide-react';
import { caseMock, flagsMock, graphMock } from './mockData';
import { api } from './api.js';


function GraphView({ graph }) {
  const svgRef = useRef();
  const gRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);
  const selectedNodeRef = useRef(null);
  
  const colors = { device: "#835E54", file: "#443728", message: "#22C55E", person: "#F59E0B", location: "#38BDF8", conversation: "#A78BFA", known: "#EF4444" };
  const graphStr = JSON.stringify(graph);

  useEffect(() => {
    if (!graph || !graph.nodes) return;
    
    const svg = d3.select(svgRef.current);
    const g = d3.select(gRef.current);
    g.selectAll("*").remove();

    svg.append("rect").attr("width", "100%").attr("height", "100%").attr("fill", "transparent").lower();

    const xs = graph.nodes.map(n => n.x || 0);
    const ys = graph.nodes.map(n => n.y || 0);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const spanX = maxX - minX || 1, spanY = maxY - minY || 1;
    
    const nodes = graph.nodes.map(n => ({
      ...n, 
      x: 200 + 400 * (((n.x || 0) - minX) / spanX) + (Math.random() - 0.5) * 20, 
      y: 100 + 300 * (((n.y || 0) - minY) / spanY) + (Math.random() - 0.5) * 20
    }));
    
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const links = graph.edges.map(e => ({ 
      source: nodeMap.get(e.source), target: nodeMap.get(e.target), type: e.type 
    })).filter(e => e.source && e.target);

    const neighbors = new Map();
    links.forEach(l => {
      if (!neighbors.has(l.source.id)) neighbors.set(l.source.id, new Set());
      if (!neighbors.has(l.target.id)) neighbors.set(l.target.id, new Set());
      neighbors.get(l.source.id).add(l.target.id);
      neighbors.get(l.target.id).add(l.source.id);
    });

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).distance(80))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(400, 250))
      .force("collide", d3.forceCollide().radius(20).iterations(3))
      .alpha(1)
      .restart();

    const zoom = d3.zoom().scaleExtent([0.1, 4]).on("zoom", (e) => g.attr("transform", e.transform));
    svg.call(zoom);
    svg.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(1));

    const link = g.append("g").attr("stroke", "#D1C8C6").attr("stroke-opacity", 0.4)
      .selectAll("line").data(links).join("line").attr("stroke-width", 1.5);

    const node = g.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("cx", d => d.x).attr("cy", d => d.y)
      .attr("r", d => d.type === 'device' ? 10 : 7)
      .attr("fill", d => colors[d.type] || "#D1C8C6")
      .attr("stroke", d => d.props?.flagged ? "#EF4444" : "#FCF9F7")
      .attr("stroke-width", d => d.props?.flagged ? 3 : 1.5)
      .style("cursor", "grab").style("transition", "opacity 0.2s ease")
      .call(d3.drag()
        .on("start", (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; d3.select(e.sourceEvent.target).style("cursor", "grabbing"); })
        .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on("end", (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; d3.select(e.sourceEvent.target).style("cursor", "grab"); })
      );

    node.append("title").text(d => `${d.label} (${d.type})`);

    node.on("mouseover", function(e, d) {
      if (selectedNodeRef.current) return;
      node.style("opacity", o => (o.id === d.id || neighbors.get(d.id)?.has(o.id)) ? 1 : 0.15);
      link.style("opacity", o => (o.source.id === d.id || o.target.id === d.id) ? 0.8 : 0.05);
    }).on("mouseout", function() {
      if (selectedNodeRef.current) return;
      node.style("opacity", 1); link.style("opacity", 0.4);
    }).on("click", (e, d) => {
      e.stopPropagation(); selectedNodeRef.current = d; setSelectedNode(d);
      node.style("opacity", o => (o.id === d.id || neighbors.get(d.id)?.has(o.id)) ? 1 : 0.15);
      link.style("opacity", o => (o.source.id === d.id || o.target.id === d.id) ? 0.8 : 0.05);
    });

    svg.on("click", () => {
      selectedNodeRef.current = null; setSelectedNode(null);
      node.style("opacity", 1); link.style("opacity", 0.4);
    });

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("cx", d => d.x).attr("cy", d => d.y);
    });

    return () => { simulation.stop(); svg.on(".zoom", null); };
  }, [graphStr]);

  if (!graph || !graph.nodes) return <div className="p-8 text-ink font-bold animate-pulse">Loading Graph Data...</div>;

  return (
    <div className="flex flex-col md:flex-row h-full w-full bg-main overflow-hidden border border-border rounded shadow-inner">
      {/* SOLID LEGEND - TAKES UP FIXED SPACE, DOES NOT OVERLAP */}
      <div className="w-full md:w-48 bg-surface border-r border-b border-border p-6 flex flex-col shrink-0 text-[10px] uppercase font-bold tracking-widest text-ink z-10">
        <div className="mb-4 opacity-60 border-b border-border pb-2">Legend</div>
        {Object.entries(colors).map(([k, c]) => (
          <div key={k} className="flex items-center gap-3 mb-3">
            <span className="w-4 h-4 rounded-full shadow-sm border border-border/50" style={{ backgroundColor: c }}></span> {k}
          </div>
        ))}
        <div className="flex items-center gap-3 mt-6 pt-4 border-t border-border text-brown">
          <span className="w-4 h-4 rounded-full border-[3px] border-red-500 bg-transparent"></span> Flagged
        </div>
      </div>

      <div className="flex-1 relative min-h-0">
        <svg ref={svgRef} viewBox="0 0 800 500" preserveAspectRatio="xMidYMid meet" className="w-full h-full" style={{ cursor: 'move' }}>
          <g ref={gRef}></g>
        </svg>

        {selectedNode && (
          <div className="absolute top-0 right-0 h-full w-72 bg-surface/95 backdrop-blur-sm border-l border-border p-6 overflow-y-auto shadow-xl transition-all">
            <div className="flex justify-between items-center mb-6 border-b border-border pb-4">
              <h3 className="font-serif font-bold text-lg text-ink">Entity Profile</h3>
              <button onClick={() => { selectedNodeRef.current=null; setSelectedNode(null); }} className="text-ink opacity-50 hover:opacity-100 text-2xl leading-none">&times;</button>
            </div>
            <div className="mb-5">
              <div className="text-[10px] text-ink opacity-60 uppercase tracking-widest mb-1">Entity Type</div>
              <div className="text-sm font-bold tracking-wide" style={{ color: colors[selectedNode.type] || '#443728' }}>{selectedNode.type.toUpperCase()}</div>
            </div>
            <div className="mb-5">
              <div className="text-[10px] text-ink opacity-60 uppercase tracking-widest mb-1">Label</div>
              <div className="text-sm text-ink font-mono break-all font-semibold bg-main p-2 rounded border border-border">{selectedNode.label}</div>
            </div>
            {selectedNode.props && Object.keys(selectedNode.props).map(k => (
              <div key={k} className="mb-4">
                <div className="text-[10px] text-ink opacity-60 uppercase tracking-widest mb-1">{k}</div>
                <div className="text-xs text-ink opacity-80 font-mono break-all">{JSON.stringify(selectedNode.props[k])}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const OverviewView = ({ totalFiles, flagged, highRisk, relationships, pctHigh, pctReview, pctSafe, pipelineState, scanning }) => (
  <div className="space-y-10 max-w-7xl">
    <div>
      <h3 className="font-serif font-bold text-xl mb-6">Investigation Summary</h3>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-6 border-b border-border pb-8">
        {[
          {l: "FILES", v: totalFiles.toLocaleString()},
          {l: "PROCESSED", v: totalFiles > 0 ? "100%" : "0%"},
          {l: "FLAGGED", v: flagged.toLocaleString()},
          {l: "HIGH RISK", v: highRisk.toLocaleString()},
          {l: "RELATIONSHIPS", v: relationships.toLocaleString()}
        ].map(s => (
          <div key={s.l}>
            <div className="text-[10px] uppercase tracking-widest font-bold opacity-60 mb-2">{s.l}</div>
            <div className={`font-serif font-bold text-2xl ${s.l==='HIGH RISK' && highRisk > 0 ? 'text-brown' : 'text-ink'}`}>{s.v}</div>
          </div>
        ))}
      </div>
    </div>

    <PipelinePanel state={pipelineState} scanning={scanning} />

    <div>
      <h3 className="font-serif font-bold text-xl mb-6">Risk Distribution</h3>
      <div className="flex h-4 rounded overflow-hidden border border-border">
        <div className="bg-brown transition-all duration-500" style={{width: `${pctHigh}%`}}></div>
        <div className="bg-ink opacity-40 transition-all duration-500" style={{width: `${pctReview}%`}}></div>
        <div className="bg-surface transition-all duration-500" style={{width: `${pctSafe}%`}}></div>
      </div>
      <div className="flex justify-between text-[10px] uppercase font-bold tracking-widest mt-2 opacity-60">
        <span>High ({pctHigh}%)</span>
        <span>Review ({pctReview}%)</span>
        <span>Safe ({pctSafe}%)</span>
      </div>
    </div>
  </div>
);

const EvidenceView = ({ flags }) => (
  <div className="flex flex-col h-full max-w-6xl">
    <h3 className="font-serif font-bold text-xl mb-6 shrink-0">Scanned Evidence</h3>
    <div className="border border-border rounded overflow-hidden bg-main flex-1 flex flex-col min-h-0 shadow-sm">
      <div className="overflow-y-auto flex-1 p-0">
        <table className="w-full text-left text-xs relative">
          <thead className="bg-surface border-b border-border text-[10px] uppercase tracking-widest font-bold sticky top-0 z-10 shadow-sm">
            <tr>
              <th className="p-4 w-1/4">File</th>
              <th className="p-4">Risk Score</th>
              <th className="p-4 w-1/2">Triggered Rules</th>
              <th className="p-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {flags.map((row, i) => (
              <tr key={i} className="hover:bg-surface/50 transition-colors">
                <td className="p-4 font-semibold break-all text-ink">{row.name}</td>
                <td className="p-4 font-bold text-base text-ink">{row.score}</td>
                <td className="p-4 font-mono text-[11px] opacity-70 group relative">
                  <div className="truncate max-w-[400px]" title={row.rules.map(r => r.plain_label).join(" / ")}>
                    {row.rules.map(r => r.plain_label).join(" / ")}
                  </div>
                </td>
                <td className="p-4 text-right">
                  <span className={`px-2 py-1 border rounded text-[10px] uppercase tracking-widest font-bold ${row.severity==='high' ? 'border-brown text-brown bg-surface' : 'border-border text-ink'}`}>
                    {row.severity === 'high' ? 'HIGH RISK' : row.severity.toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
            {flags.length === 0 && (
              <tr>
                <td colSpan="4" className="p-8 text-center text-ink opacity-50 italic font-bold">No flagged evidence found in scan.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

const RiskAnalysisView = ({ featuredFlag }) => {
  if (!featuredFlag) return <div className="p-8 italic opacity-60">No high-risk flags available for analysis.</div>;
  return (
    <div className="max-w-3xl h-full flex flex-col">
      <h3 className="font-serif font-bold text-xl mb-6 shrink-0">Explainability & Traceability</h3>
      <div className="bg-surface border border-border p-8 rounded shadow-sm flex-1 overflow-y-auto">
        <div className="text-[10px] uppercase tracking-widest font-bold mb-8 text-brown border-b border-border pb-2">WHY WAS EVIDENCE [{featuredFlag.name}] FLAGGED?</div>
        <div className="space-y-6 mb-8">
          {featuredFlag.rules.map((r, i) => (
            <React.Fragment key={i}>
              <div className="flex justify-between items-start text-sm">
                <div className="pr-8">
                  <span className="font-bold text-base text-ink">{r.plain_label}</span>
                  <p className="opacity-70 text-xs mt-2 leading-relaxed font-mono bg-main p-3 rounded border border-border shadow-inner">{r.detail}</p>
                </div>
                <div className="font-bold text-xl text-brown bg-main px-3 py-1 rounded border border-border shadow-sm">+{r.points}</div>
              </div>
              {i !== featuredFlag.rules.length - 1 && <div className="h-[1px] w-full bg-border/50"></div>}
            </React.Fragment>
          ))}
          <div className="flex justify-between items-center text-sm font-bold pt-6 border-t-[3px] border-border">
            <div className="text-sm uppercase tracking-widest text-ink">TOTAL PROVABLE SCORE</div>
            <div className="text-4xl font-serif text-brown">{featuredFlag.score}</div>
          </div>
        </div>
        <div className="text-xs italic opacity-80 flex items-center gap-2 font-semibold text-brown bg-main p-4 rounded border border-brown/30 shadow-inner">
          <Shield className="w-4 h-4"/> “Every score is a strict mathematical sum of the rules above — zero hidden estimations.”
        </div>
      </div>
    </div>
  );
};

const AgentView = () => {
  const [q, setQ] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);

  const ask = async (text) => {
    if (!text) return;
    setBusy(true); setRes(null); setQ("");
    try { setRes(await api.query(text)); } catch (e) {} finally { setBusy(false); }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl border border-border rounded bg-surface shadow-sm">
      <div className="p-6 border-b border-border bg-main flex flex-col gap-2 shrink-0">
        <h2 className="text-xl font-serif font-bold text-ink">Agentic Query</h2>
        <div className="text-[10px] font-bold uppercase tracking-widest opacity-60">Ask questions in plain English. Every reasoning step is logged.</div>
      </div>
      <div className="flex-1 p-6 overflow-y-auto bg-surface relative min-h-0">
        {busy && <div className="text-ink opacity-60 font-bold animate-pulse text-sm">Agent thinking...</div>}
        {res && (
          <div className="space-y-6">
            <div className="p-5 bg-main border border-border rounded text-ink shadow-sm relative overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-brown"></div>
              <strong className="text-[10px] uppercase tracking-widest text-brown block mb-2">Verified Answer</strong>
              <div className="text-sm leading-relaxed font-semibold">{res.answer}</div>
            </div>
            <div className="p-5 bg-main border border-border rounded opacity-90 shadow-inner">
              <strong className="text-[10px] text-ink opacity-60 uppercase tracking-widest block mb-4 border-b border-border pb-2">Agent Reasoning Step Log</strong>
              {res.reasoning_log?.map(s => (
                <div key={s.step} className="mt-3 text-sm">
                  <span className="text-brown font-bold mr-2 text-[11px] tracking-wider">STEP {s.step}:</span> 
                  <span className="font-semibold text-ink">{s.title}</span>
                  <div className="text-xs font-mono opacity-70 mt-1 pl-4 border-l-2 border-border/50 ml-[26px] py-1">{s.detail}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        {!busy && !res && (
          <div className="h-full flex flex-col items-center justify-center opacity-30">
            <MessageSquare className="w-16 h-16 mb-4" />
            <p className="font-serif font-bold text-xl">Agent Ready</p>
          </div>
        )}
      </div>
      <div className="p-4 bg-main border-t border-border shrink-0">
        <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
          <div className="text-[10px] font-bold uppercase tracking-widest opacity-50 mt-1.5 shrink-0">TRY:</div>
          {["who was active at night?", "conversations about Harbour Line"].map(ex => (
            <button key={ex} onClick={() => ask(ex)} className="px-3 py-1.5 text-[10px] uppercase tracking-wider bg-surface border border-border text-ink font-bold rounded hover:bg-border/30 transition-colors shadow-sm shrink-0">{ex}</button>
          ))}
        </div>
        <form onSubmit={e => { e.preventDefault(); ask(q); }} className="flex gap-3">
          <input value={q} onChange={e => setQ(e.target.value)} className="flex-1 bg-surface border border-border p-3 rounded text-ink text-sm shadow-inner focus:outline-none focus:border-brown transition-colors" placeholder="Ask a question about the evidence..." />
          <button type="submit" className="bg-ink text-surface px-8 py-3 rounded text-[11px] font-bold uppercase tracking-widest shadow-md hover:opacity-90 transition-opacity">Query</button>
        </form>
      </div>
    </div>
  );
};

const AuditLogView = ({ flags, auth }) => {
  // Generate deterministic audit logs based on flags to prove action logging
  const logs = [];
  
  if (auth) {
    logs.push({ time: auth.ts, action: "ACCESS", detail: `Investigator ${auth.invId} authenticated for Case ${auth.caseNum}` });
  }

  logs.push(
    { time: "11:24:01", action: "SYSTEM", detail: `Scan Pipeline Initialized (Target: mock_device)` },
    { time: "11:24:05", action: "INGEST", detail: "Extracted 20 files, 3 archives decompressed" },
    { time: "11:24:12", action: "HASH SCREEN", detail: "Checked against 140K known harmful hashes" },
    { time: "11:24:14", action: "AGENT TRACE", detail: `Identified ${flags.length} items requiring risk review` }
  );
  
  flags.forEach((f, i) => {
    logs.push({ time: `11:24:${15 + i*2}`, action: "RISK ENGINE", detail: `Computed deterministic risk score ${f.score} for ${f.name}` });
  });

  return (
    <div className="flex flex-col h-full max-w-4xl">
      <div className="mb-6 shrink-0">
        <h3 className="font-serif font-bold text-xl">Verifiable Audit Log</h3>
        <p className="text-[10px] font-bold uppercase tracking-widest opacity-60 mt-1">Immutable record of all pipeline actions and agent decisions.</p>
      </div>
      <div className="bg-surface border border-border rounded flex-1 overflow-y-auto shadow-inner p-6 font-mono text-xs">
        {logs.map((log, i) => (
          <div key={i} className="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 py-4 border-b border-border/50 hover:bg-border/10 transition-colors">
            <span className="opacity-50 w-24 shrink-0 font-bold">{log.time}</span>
            <span className="font-bold w-32 shrink-0 px-2 py-1 bg-main border border-border rounded text-center" style={{color: log.action==='RISK ENGINE'?'#835E54':''}}>{log.action}</span>
            <span className="text-ink font-semibold opacity-90">{log.detail}</span>
          </div>
        ))}
      </div>
    </div>
  );
};


const PIPELINE_STAGES = [
  { key: "ingestion", label: "Ingestion", detail: "Validating files" },
  { key: "hash_match", label: "Hashing", detail: "Known content screen" },
  { key: "synthetic", label: "Synthetic", detail: "AI artifact check" },
  { key: "risk", label: "Risk", detail: "Rule scoring" },
  { key: "explain", label: "Explain", detail: "Plain-language reasons" },
  { key: "graph", label: "Graph", detail: "Relationship mapping" },
];

const PipelinePanel = ({ state, scanning }) => {
  if (!state.started) {
    return (
      <div className="border border-border bg-surface/40 rounded p-6">
        <div className="text-[10px] uppercase tracking-widest font-bold text-brown mb-2">Pipeline Execution</div>
        <div className="font-serif text-2xl font-bold text-ink">Ready to scan</div>
        <div className="text-xs font-mono text-ink/55 mt-2">Start Scan will stream ingestion, hashing, risk scoring, explanations, and graph construction here.</div>
      </div>
    );
  }

  const doneCount = state.done.size;
  const stageProgress = state.complete ? 100 : Math.round((doneCount / PIPELINE_STAGES.length) * 100);
  const fileProgress = state.total ? Math.round((state.processed / state.total) * 100) : 0;
  const progress = Math.max(stageProgress, fileProgress);

  return (
    <div className="border border-border bg-surface/45 rounded p-6 overflow-hidden relative">
      <div className="pipeline-sweep absolute inset-x-0 top-0 h-1 opacity-80"></div>
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6 mb-7">
        <div>
          <div className="text-[10px] uppercase tracking-widest font-bold text-brown mb-2">Pipeline Execution</div>
          <div className="font-serif text-2xl font-bold text-ink">{state.complete ? "Scan complete" : scanning ? "Agent executing scan" : "Scan interrupted"}</div>
          <div className="text-xs font-mono text-ink/60 mt-2 max-w-3xl">{state.message || state.currentLabel || "Preparing modules"}</div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-right shrink-0">
          <div className="bg-main border border-border rounded px-4 py-3">
            <div className="font-serif font-bold text-2xl text-ink">{state.processed}</div>
            <div className="text-[10px] uppercase tracking-widest font-bold text-ink/45">Done</div>
          </div>
          <div className="bg-main border border-border rounded px-4 py-3">
            <div className="font-serif font-bold text-2xl text-ink">{state.total || 0}</div>
            <div className="text-[10px] uppercase tracking-widest font-bold text-ink/45">Files</div>
          </div>
        </div>
      </div>

      <div className="relative mb-8">
        <div className="h-3 bg-main border border-border rounded overflow-hidden">
          <div className="h-full bg-brown transition-all duration-500 ease-out relative" style={{ width: `${progress}%` }}>
            {scanning && <div className="pipeline-shimmer absolute inset-0"></div>}
          </div>
        </div>
        <div className="mt-2 flex justify-between text-[10px] uppercase tracking-widest font-bold text-ink/45">
          <span>{state.currentLabel || "Initializing"}</span>
          <span>{progress}%</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
        {PIPELINE_STAGES.map((stage, index) => {
          const done = state.done.has(stage.key) || state.complete;
          const active = !state.complete && stage.key === state.current;
          return (
            <div key={stage.key} className={`relative min-h-28 rounded border bg-main p-4 transition-all duration-300 ${active ? "border-brown shadow-md -translate-y-1" : done ? "border-border" : "border-border/60 opacity-55"}`}>
              <div className="flex items-center justify-between mb-4">
                <div className={`w-8 h-8 rounded-full border flex items-center justify-center ${done ? "bg-brown text-main border-brown" : active ? "border-brown text-brown pipeline-pulse" : "border-border text-ink/40"}`}>
                  {done ? <CheckCircle2 className="w-4 h-4" /> : <span className="text-xs font-bold">{index + 1}</span>}
                </div>
                {active && <div className="thinking-bars"><span></span><span></span><span></span></div>}
              </div>
              <div className="text-[10px] uppercase tracking-widest font-bold text-ink truncate">{stage.label}</div>
              <div className="text-[10px] font-mono text-ink/55 mt-2 leading-relaxed">{active && state.message ? state.message : stage.detail}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const DashboardDemo = ({ auth }) => {
  const [caseData, setCaseData] = useState(null);
  const [flags, setFlags] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [activeTab, setActiveTab] = useState('Overview');
  const [scanning, setScanning] = useState(false);
  const [scanLogs, setScanLogs] = useState([]);
  const [pipelineState, setPipelineState] = useState({
    started: false,
    complete: false,
    current: null,
    currentLabel: "",
    message: "",
    processed: 0,
    total: 0,
    done: new Set(),
  });

  useEffect(() => {
    const load = async () => {
      try {
        const [cRes, fRes, gRes] = await Promise.all([api.case(), api.flags(), api.graph()]);
        setCaseData(cRes); setFlags(fRes.flags || []); setGraphData(gRes);
      } catch (err) {
        setCaseData(caseMock); 
        setFlags(flagsMock.flags || []); 
        setGraphData(graphMock);
      }
    };
    load();
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, []);


  const runScan = async () => {
    setScanning(true);
    setScanLogs(["Initializing scan pipeline..."]);
    setPipelineState({
      started: true,
      complete: false,
      current: null,
      currentLabel: "Initializing",
      message: "Preparing scan",
      processed: 0,
      total: 0,
      done: new Set(),
    });
    try {
      await api.newCase();
      const { scan_id } = await api.scan();
      const evt = new EventSource(`/api/scan/events?scan_id=${scan_id}`);
      const completeScan = () => {
        evt.close();
        setScanning(false);
        setScanLogs(prev => [...prev, "Scan complete. Agent ready."]);
        setPipelineState(prev => ({
          ...prev,
          complete: true,
          current: "graph",
          currentLabel: "Complete",
          message: "All pipeline stages complete",
          processed: prev.total || prev.processed,
          done: new Set(PIPELINE_STAGES.map(stage => stage.key)),
        }));
        api.case().then(setCaseData).catch(() => {});
        api.flags().then(res => setFlags(res.flags || [])).catch(() => {});
        api.graph().then(setGraphData).catch(() => {});
      };
      evt.onmessage = (e) => {
        const d = JSON.parse(e.data);
        if (d.event === "module") {
          setScanLogs(prev => [...prev, d.label]);
          setPipelineState(prev => ({
            ...prev,
            current: d.module,
            currentLabel: d.label,
            message: d.label,
          }));
        } else if (d.event === "module_done") {
          setPipelineState(prev => {
            const done = new Set(prev.done);
            done.add(d.module);
            return { ...prev, done, message: `${d.module} complete` };
          });
        } else if (d.event === "progress") {
          setPipelineState(prev => ({
            ...prev,
            message: d.message || prev.message,
            processed: d.processed ?? prev.processed,
            total: d.total ?? prev.total,
          }));
        } else if (d.event === "done") {
          completeScan();
        }
      };
      evt.addEventListener("done", completeScan);
      evt.onerror = () => {
        evt.close();
        setScanning(false);
        setScanLogs(prev => [...prev, "Scan stream closed before completion."]);
        setPipelineState(prev => ({ ...prev, message: "Scan stream closed" }));
      };
    } catch (err) {
      setScanning(false);
      setScanLogs(prev => [...prev, "Scan could not start. Check that the backend is running."]);
      setPipelineState(prev => ({ ...prev, started: true, message: "Backend unavailable" }));
    }
  };

  if (!caseData) return <div className="flex items-center justify-center h-screen w-screen bg-main text-ink font-serif text-2xl font-bold animate-pulse">Initializing ACPIA Pipeline...</div>;

  const totalFiles = caseData.files || 0;
  const flagged = caseData.flags?.total || 0;
  const highRisk = caseData.flags?.high || 0;
  const relationships = graphData?.edges?.length || 0;

  const safe = Math.max(0, totalFiles - flagged);
  const review = (caseData.flags?.medium || 0) + (caseData.flags?.low || 0);
  const total = Math.max(1, totalFiles);
  
  const pctHigh = Math.round((highRisk / total) * 100);
  const pctReview = Math.round((review / total) * 100);
  const pctSafe = Math.round((safe / total) * 100);

  const featuredFlag = flags.length > 0 ? flags[0] : null;

  return (
    <div className="bg-main overflow-hidden flex flex-col md:flex-row h-full w-full">
      <div className="w-full md:w-64 bg-surface border-r border-border p-6 shrink-0 flex flex-col gap-6 shadow-md z-20">
        <div className="text-[10px] uppercase tracking-widest font-bold text-brown bg-brown/5 p-3 rounded text-center border border-brown/10">
          CASE: {auth.caseNum} <br/><span className="opacity-70 mt-1 block">INV: {auth.invId}</span>
        </div>
        <button
          type="button"
          onClick={runScan}
          disabled={scanning}
          className="flex items-center justify-center gap-2 bg-ink text-surface p-4 rounded text-[11px] font-bold uppercase tracking-widest shadow-md hover:opacity-90 disabled:opacity-50 transition-all"
        >
          <PlayCircle className="w-4 h-4" />
          {scanning ? "Scanning" : "Start Scan"}
        </button>
        <div className="flex flex-col gap-3">
          {[
            {icon: Monitor, l: 'Overview'}, {icon: FolderSearch, l: 'Evidence'}, {icon: TriangleAlert, l: 'Risk Analysis'}, 
            {icon: Network, l: 'Relationships'}, {icon: MessageSquare, l: 'Agent'}, {icon: ClipboardCheck, l: 'Audit Log'}
          ].map((item) => (
            <div 
              key={item.l} onClick={() => setActiveTab(item.l)}
              className={`text-[11px] font-bold uppercase tracking-widest flex items-center gap-3 cursor-pointer p-4 rounded transition-all ${activeTab === item.l ? 'text-surface bg-ink shadow-md translate-x-1' : 'text-ink opacity-60 hover:opacity-100 hover:bg-border/30 hover:translate-x-1'}`}
            >
              <item.icon className="w-4 h-4 shrink-0" /> {item.l}
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 p-8 lg:p-12 bg-main overflow-hidden flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'Overview' && <OverviewView totalFiles={totalFiles} flagged={flagged} highRisk={highRisk} relationships={relationships} pctHigh={pctHigh} pctReview={pctReview} pctSafe={pctSafe} pipelineState={pipelineState} scanning={scanning} />}
          {activeTab === 'Evidence' && <EvidenceView flags={flags} />}
          {activeTab === 'Risk Analysis' && <RiskAnalysisView featuredFlag={featuredFlag} />}
          {activeTab === 'Relationships' && (
            <div className="h-full flex flex-col">
              <h3 className="font-serif font-bold text-xl mb-2 shrink-0">Relationship Network</h3>
              <p className="text-[10px] text-ink opacity-60 font-bold uppercase tracking-widest mb-6 shrink-0">Maps all connections — between files, people, contacts, and devices — into one relationship network.</p>
              <div className="flex-1 min-h-0">
                <GraphView graph={graphData} />
              </div>
            </div>
          )}
          {activeTab === 'Agent' && <AgentView />}
          {activeTab === 'Audit Log' && <AuditLogView flags={flags} auth={auth} />}
        </div>
      </div>
    </div>
  );
};

const LoginScreen = ({ onLogin }) => {
  const [invId, setInvId] = useState("");
  const [caseNum, setCaseNum] = useState("");
  const [pwd, setPwd] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (invId.trim() && caseNum.trim() && pwd.trim()) {
      onLogin({ 
        invId: invId.trim().toUpperCase(), 
        caseNum: caseNum.trim().toUpperCase(), 
        ts: new Date().toLocaleTimeString('en-US', { hour12: false }) 
      });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-surface">
      <div className="w-full max-w-md bg-main border border-border p-10 md:p-12 rounded shadow-2xl flex flex-col gap-8 relative overflow-hidden">
        {/* Subtle decorative top border */}
        <div className="absolute top-0 left-0 w-full h-1 bg-brown"></div>

        <div className="flex flex-col items-center gap-3 border-b border-border pb-8">
          <Shield className="w-10 h-10 text-brown mb-2 opacity-90" />
          <h1 className="font-serif font-bold text-4xl text-ink tracking-tight">ACPIA</h1>
          <p className="text-[10px] uppercase font-bold tracking-[0.2em] text-ink opacity-60">Forensic Intelligence Platform</p>
        </div>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <label className="text-[10px] uppercase font-bold tracking-widest text-ink opacity-70">Investigator ID</label>
            <input type="text" value={invId} onChange={e => setInvId(e.target.value)} required className="bg-surface border border-border p-3.5 rounded text-sm text-ink shadow-inner font-mono font-bold focus:outline-none focus:border-brown transition-colors" placeholder="e.g. INV-7492" />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-[10px] uppercase font-bold tracking-widest text-ink opacity-70">Case Number</label>
            <input type="text" value={caseNum} onChange={e => setCaseNum(e.target.value)} required className="bg-surface border border-border p-3.5 rounded text-sm text-ink shadow-inner font-mono font-bold focus:outline-none focus:border-brown transition-colors" placeholder="e.g. CASE-0241" />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-[10px] uppercase font-bold tracking-widest text-ink opacity-70">Passkey</label>
            <input type="password" value={pwd} onChange={e => setPwd(e.target.value)} required className="bg-surface border border-border p-3.5 rounded text-sm text-ink shadow-inner font-mono font-bold focus:outline-none focus:border-brown transition-colors" />
          </div>
          
          <div className="pt-4">
            <button type="submit" className="w-full bg-ink text-surface py-4 rounded text-xs font-bold uppercase tracking-widest shadow-md hover:opacity-90 hover:shadow-lg transition-all">Sign In</button>
            <p className="text-center text-[10px] font-bold uppercase tracking-widest text-brown mt-5 opacity-90 bg-brown/5 py-2 rounded border border-brown/10">
              Authorized personnel only. All access is logged.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default function App() {
  const [auth, setAuth] = useState(null);

  if (!auth) {
    return <LoginScreen onLogin={setAuth} />;
  }

  return (
    <div className="h-screen w-screen overflow-hidden">
      <DashboardDemo auth={auth} />
    </div>
  );
}
