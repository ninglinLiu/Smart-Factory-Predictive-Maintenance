"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

const COLORS = { Healthy: "#0072B2", Watch: "#E69F00", Critical: "#D55E00" };
const SENSORS = ["sensor_11", "sensor_4", "sensor_12", "sensor_7", "sensor_15"];
const PAGES = ["Fleet Overview", "Engine Detail", "Model Insights", "Recommendations"] as const;

type Page = (typeof PAGES)[number];

type FleetEngine = {
  unit_number: number;
  true_RUL: number;
  pred_final: number;
  status: string;
  abs_error: number;
};

type EngineTraj = {
  unit_number: number;
  life_stage: string;
  cycles: number[];
  sensors: Record<string, number[]>;
  sensor_11_roll20: number[];
  pred_rul: number[];
  last_rul: number;
  status: string;
};

function statusClass(s: string) {
  if (s === "Critical") return "status-critical";
  if (s === "Watch") return "status-watch";
  return "status-healthy";
}

function bandFromRul(rul: number, threshold: number) {
  if (rul < threshold) return "Critical";
  if (rul < 60) return "Watch";
  return "Healthy";
}

export default function Dashboard() {
  const [page, setPage] = useState<Page>("Fleet Overview");
  const [loading, setLoading] = useState(true);
  const [fleet, setFleet] = useState<{ threshold: number; engines: FleetEngine[]; summary: Record<string, string | number> } | null>(null);
  const [engines, setEngines] = useState<{ engines: Record<string, EngineTraj>; life_stages: Record<string, number[]> } | null>(null);
  const [fi, setFi] = useState<{ feature: string; perm_importance_mean: number }[]>([]);
  const [recs, setRecs] = useState<Record<string, string>[]>([]);

  const [threshold, setThreshold] = useState(30);
  const [riskFilter, setRiskFilter] = useState("All");
  const [lifeStage, setLifeStage] = useState("All");
  const [selectedEngines, setSelectedEngines] = useState<number[]>([1, 2, 3]);
  const [sensor, setSensor] = useState("sensor_11");
  const [drillEngine, setDrillEngine] = useState(1);

  useEffect(() => {
    Promise.all([
      fetch("/data/fleet.json").then((r) => r.json()),
      fetch("/data/engines.json").then((r) => r.json()),
      fetch("/data/feature_importance.json").then((r) => r.json()),
      fetch("/data/recommendations.json").then((r) => r.json()),
    ]).then(([f, e, featureImp, recommendations]) => {
      setFleet(f);
      setEngines(e);
      setFi(featureImp);
      setRecs(recommendations);
      setThreshold(f.threshold);
      setLoading(false);
    });
  }, []);

  const fleetFiltered = useMemo(() => {
    if (!fleet) return [];
    return fleet.engines
      .map((row) => ({
        ...row,
        status: bandFromRul(row.pred_final, threshold),
      }))
      .filter((row) => riskFilter === "All" || row.status === riskFilter)
      .sort((a, b) => a.pred_final - b.pred_final);
  }, [fleet, threshold, riskFilter]);

  const engineIds = useMemo(() => {
    if (!engines) return [];
    return Object.keys(engines.engines).map(Number).sort((a, b) => a - b);
  }, [engines]);

  const detailEngines = useMemo(() => {
    let ids = selectedEngines.length ? selectedEngines : [drillEngine];
    if (lifeStage !== "All" && engines) {
      const stageSet = new Set(engines.life_stages[lifeStage] || []);
      ids = ids.filter((id) => stageSet.has(id));
    }
    if (!ids.includes(drillEngine)) ids = [drillEngine, ...ids.filter((x) => x !== drillEngine)];
    return ids.slice(0, 5);
  }, [selectedEngines, drillEngine, lifeStage, engines]);

  const plotLayout = {
    paper_bgcolor: "#0e1117",
    plot_bgcolor: "#0e1117",
    font: { color: "#fafafa" },
    margin: { t: 40, r: 20, b: 50, l: 50 },
    legend: { orientation: "h" as const, y: -0.15 },
  };

  if (loading) {
    return (
      <div className="main" style={{ padding: "3rem" }}>
        Loading dashboard data…
      </div>
    );
  }

  const summary = fleet!.summary;
  const criticalCount = fleet!.engines.filter((e) => e.pred_final < threshold).length;
  const meanRul = fleet!.engines.reduce((s, e) => s + e.pred_final, 0) / fleet!.engines.length;

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <h2>Dashboard</h2>
        <nav className="nav">
          {PAGES.map((p) => (
            <button key={p} className={page === p ? "active" : ""} onClick={() => setPage(p)}>
              {p}
            </button>
          ))}
        </nav>

        <h2>Global Filters</h2>
        <label>RUL risk threshold (cycles): {threshold}</label>
        <input type="range" min={10} max={60} value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} />

        <label>Risk band filter</label>
        <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
          {["All", "Critical", "Watch", "Healthy"].map((o) => (
            <option key={o}>{o}</option>
          ))}
        </select>

        <label>Life-stage filter (train fleet)</label>
        <select value={lifeStage} onChange={(e) => setLifeStage(e.target.value)}>
          {["All", "early", "mid", "late"].map((o) => (
            <option key={o}>{o}</option>
          ))}
        </select>

        <label>Engines to inspect</label>
        <select
          multiple
          size={5}
          value={selectedEngines.map(String)}
          onChange={(e) =>
            setSelectedEngines(Array.from(e.target.selectedOptions, (o) => Number(o.value)))
          }
        >
          {engineIds.map((id) => (
            <option key={id} value={id}>
              Engine {id}
            </option>
          ))}
        </select>

        <label>Primary sensor</label>
        <select value={sensor} onChange={(e) => setSensor(e.target.value)}>
          {SENSORS.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>

        <div className="legend">
          <strong>Risk legend (colorblind-friendly)</strong>
          <p style={{ color: COLORS.Healthy }}>Healthy — RUL ≥ 60 cycles</p>
          <p style={{ color: COLORS.Watch }}>Watch — 30 ≤ RUL &lt; 60 cycles</p>
          <p style={{ color: COLORS.Critical }}>Critical — RUL &lt; 30 cycles</p>
        </div>
      </aside>

      <main className="main">
        <h1>Smart Factory Predictive Maintenance Dashboard</h1>
        <p className="caption">NASA C-MAPSS FD001 — Assignment 2 | Colorblind-friendly R/Y/G risk bands</p>

        {page === "Fleet Overview" && (
          <>
            <h2>Fleet Overview</h2>
            <div className="kpi-row">
              <div className="kpi">
                <div className="label">Engines Monitored</div>
                <div className="value">{summary.engines_monitored}</div>
              </div>
              <div className="kpi">
                <div className="label">Mean Predicted RUL</div>
                <div className="value">{meanRul.toFixed(0)} cycles</div>
              </div>
              <div className="kpi">
                <div className="label">Critical (below threshold)</div>
                <div className="value">{criticalCount}</div>
              </div>
              <div className="kpi">
                <div className="label">Model Test MAE</div>
                <div className="value">{summary.test_mae} cycles</div>
              </div>
              <div className="kpi">
                <div className="label">Features Used</div>
                <div className="value">{summary.n_features}</div>
              </div>
            </div>

            <Plot
              data={[
                {
                  type: "histogram",
                  x: fleet!.engines.map((e) => e.pred_final),
                  marker: {
                    color: fleet!.engines.map((e) => COLORS[bandFromRul(e.pred_final, threshold) as keyof typeof COLORS]),
                  },
                  nbinsx: 20,
                },
              ]}
              layout={{
                ...plotLayout,
                title: "Predicted RUL at Last Cycle — by Risk Band",
                xaxis: { title: "Predicted RUL (cycles)" },
                shapes: [
                  {
                    type: "line",
                    x0: threshold,
                    x1: threshold,
                    y0: 0,
                    y1: 1,
                    yref: "paper",
                    line: { dash: "dash", color: "#888" },
                  },
                ],
              }}
              style={{ width: "100%", height: 360 }}
              config={{ displayModeBar: false }}
            />

            <div className="grid-2">
              <div>
                <h3>Actual vs Predicted</h3>
                <Plot
                  data={[
                    {
                      type: "scatter",
                      mode: "markers",
                      x: fleetFiltered.map((e) => e.true_RUL),
                      y: fleetFiltered.map((e) => e.pred_final),
                      text: fleetFiltered.map((e) => `Engine ${e.unit_number}`),
                      marker: {
                        color: fleetFiltered.map((e) => COLORS[e.status as keyof typeof COLORS]),
                        size: 8,
                      },
                    },
                    {
                      type: "scatter",
                      mode: "lines",
                      x: [0, Math.max(...fleetFiltered.map((e) => e.true_RUL))],
                      y: [0, Math.max(...fleetFiltered.map((e) => e.true_RUL))],
                      line: { dash: "dash", color: "#666" },
                      name: "Perfect",
                    },
                  ]}
                  layout={{ ...plotLayout, title: "Test Set Accuracy (filtered fleet)", xaxis: { title: "True RUL" }, yaxis: { title: "Pred RUL" } }}
                  style={{ width: "100%", height: 380 }}
                  config={{ displayModeBar: false }}
                />
              </div>
              <div>
                <h3>Fleet Risk Table — drill-down</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Engine</th>
                      <th>Pred RUL</th>
                      <th>True RUL</th>
                      <th>Status</th>
                      <th>Abs Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fleetFiltered.slice(0, 15).map((row) => (
                      <tr key={row.unit_number}>
                        <td>{row.unit_number}</td>
                        <td>{row.pred_final.toFixed(1)}</td>
                        <td>{row.true_RUL.toFixed(0)}</td>
                        <td className={statusClass(row.status)}>{row.status}</td>
                        <td>{row.abs_error.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <label style={{ display: "block", marginTop: "1rem" }}>
                  Drill-down: select engine for Engine Detail page
                </label>
                <select value={drillEngine} onChange={(e) => setDrillEngine(Number(e.target.value))}>
                  {fleetFiltered.map((e) => (
                    <option key={e.unit_number} value={e.unit_number}>
                      Engine {e.unit_number}
                    </option>
                  ))}
                </select>
                <button
                  style={{ marginTop: "0.5rem", padding: "0.5rem 1rem", cursor: "pointer" }}
                  onClick={() => {
                    setSelectedEngines([drillEngine]);
                    setPage("Engine Detail");
                  }}
                >
                  Go to Engine Detail
                </button>
              </div>
            </div>
          </>
        )}

        {page === "Engine Detail" && engines && (
          <>
            <h2>Engine Detail</h2>
            {detailEngines.map((uid) => {
              const eng = engines.engines[String(uid)];
              if (!eng) return null;
              const status = bandFromRul(eng.last_rul, threshold);
              const roll = eng.sensor_11_roll20;
              return (
                <div key={uid} style={{ marginBottom: "2rem" }}>
                  <h3>
                    Engine {uid} — <span className={statusClass(status)}>{status}</span> (predicted RUL {eng.last_rul} cycles)
                  </h3>
                  <div className="grid-2">
                    <Plot
                      data={[
                        { type: "scatter", mode: "lines", x: eng.cycles, y: eng.sensors[sensor], name: sensor, line: { color: "#0072B2" } },
                        ...(roll.length
                          ? [{ type: "scatter", mode: "lines", x: eng.cycles, y: roll, name: "20-cycle rolling mean", line: { dash: "dash", color: "#E69F00" } }]
                          : []),
                      ]}
                      layout={{ ...plotLayout, title: `${sensor} trend`, xaxis: { title: "Cycle" } }}
                      style={{ width: "100%", height: 320 }}
                      config={{ displayModeBar: false }}
                    />
                    <Plot
                      data={[{ type: "scatter", mode: "lines", x: eng.cycles, y: eng.pred_rul, name: "Predicted RUL", line: { color: "#D55E00" } }]}
                      layout={{
                        ...plotLayout,
                        title: "Predicted RUL trajectory",
                        xaxis: { title: "Cycle" },
                        yaxis: { title: "RUL (cycles)" },
                        shapes: [
                          { type: "line", x0: eng.cycles[0], x1: eng.cycles[eng.cycles.length - 1], y0: threshold, y1: threshold, line: { dash: "dot", color: "#E69F00" } },
                          { type: "line", x0: eng.cycles[0], x1: eng.cycles[eng.cycles.length - 1], y0: 60, y1: 60, line: { dash: "dot", color: "#0072B2" } },
                        ],
                      }}
                      style={{ width: "100%", height: 320 }}
                      config={{ displayModeBar: false }}
                    />
                  </div>
                  {status === "Critical" && (
                    <div className="alert error">
                      MAINTENANCE: Schedule inspection for Engine {uid} — RUL {eng.last_rul} &lt; {threshold} cycles (Critical).
                    </div>
                  )}
                  {status === "Watch" && (
                    <div className="alert warn">WATCH: Engine {uid} entering degradation window (RUL {eng.last_rul} cycles).</div>
                  )}
                  {status === "Healthy" && (
                    <div className="alert ok">HEALTHY: Engine {uid} — RUL {eng.last_rul} cycles.</div>
                  )}
                </div>
              );
            })}
          </>
        )}

        {page === "Model Insights" && (
          <>
            <h2>Model Insights</h2>
            <Plot
              data={[
                {
                  type: "bar",
                  orientation: "h",
                  y: fi.map((f) => f.feature).reverse(),
                  x: fi.map((f) => f.perm_importance_mean).reverse(),
                  marker: { color: "#0072B2" },
                },
              ]}
              layout={{ ...plotLayout, title: "Top 15 features — final Random Forest model", xaxis: { title: "Permutation importance" } }}
              style={{ width: "100%", height: 480 }}
              config={{ displayModeBar: false }}
            />
            <h3>Error Analysis — filtered fleet worst predictions</h3>
            <table>
              <thead>
                <tr>
                  <th>Engine</th>
                  <th>True RUL</th>
                  <th>Pred RUL</th>
                  <th>Status</th>
                  <th>Abs Error</th>
                </tr>
              </thead>
              <tbody>
                {[...fleetFiltered]
                  .sort((a, b) => b.abs_error - a.abs_error)
                  .slice(0, 10)
                  .map((row) => (
                    <tr key={row.unit_number}>
                      <td>{row.unit_number}</td>
                      <td>{row.true_RUL.toFixed(0)}</td>
                      <td>{row.pred_final.toFixed(1)}</td>
                      <td className={statusClass(row.status)}>{row.status}</td>
                      <td>{row.abs_error.toFixed(1)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </>
        )}

        {page === "Recommendations" && (
          <>
            <h2>Business Recommendations</h2>
            <p className="caption">Prioritised for Maintenance Director and Plant Manager.</p>
            {recs.map((row) => (
              <details key={row.id} className="rec" open={row.priority === "High"}>
                <summary>
                  {row.priority === "High" ? "🔴" : row.priority === "Medium" ? "🟡" : "🟢"} {row.id}: {row.title} [{row.priority}]
                </summary>
                <div className="body">
                  <p><strong>Problem:</strong> {row.problem}</p>
                  <p><strong>Solution:</strong> {row.solution}</p>
                  <p><strong>Expected Impact:</strong> {row.expected_impact}</p>
                  <p><strong>Implementation:</strong> {row.implementation}</p>
                  <p><strong>Timeline:</strong> {row.timeline} | <strong>Owner:</strong> {row.owner}</p>
                  <p><strong>Evidence:</strong> {row.evidence}</p>
                </div>
              </details>
            ))}
          </>
        )}
      </main>
    </div>
  );
}
