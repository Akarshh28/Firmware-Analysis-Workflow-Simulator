"use client";
import React, { useEffect, useState } from "react";
import { useProjectStore } from "../store/projectStore";
import api from "../services/api";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
} from "recharts";
import {
  ShieldAlert,
  TrendingUp,
  FileSearch,
  Cpu,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
} from "lucide-react";

type DashboardSummary = {
  critical?: number;
  high?: number;
  medium?: number;
  low?: number;
  riskScore?: number;
  riskLabel?: string;
  riskSummary?: string;
};

type DashboardMetrics = {
  totalFindings?: number | string;
  criticalIssues?: number | string;
  stagesCompleted?: string;
  duration?: string;
};

type DashboardFinding = {
  id?: string;
  title?: string;
  severity?: string;
  stage?: string;
  tool?: string;
};

type DashboardPipelinePoint = {
  name?: string;
  issues?: number;
  stage?: string;
  mins?: number;
  value?: number;
  fill?: string;
};

type DashboardPipeline = {
  vulnerabilities?: DashboardPipelinePoint[];
  timeline?: DashboardPipelinePoint[];
  severity?: DashboardPipelinePoint[];
};

type DashboardData = {
  summary?: DashboardSummary;
  metrics?: DashboardMetrics;
  findings?: DashboardFinding[];
  pipeline?: DashboardPipeline;
  logs?: unknown[];
};

const fallbackSummary: DashboardSummary = {
  critical: 4,
  high: 9,
  medium: 14,
  low: 8,
  riskScore: 32,
  riskLabel: "CRITICAL RISK",
  riskSummary:
    "Firmware poses significant security risk. 4 critical vulnerabilities must be patched before deployment.",
};

const fallbackMetrics: DashboardMetrics = {
  totalFindings: 35,
  criticalIssues: 4,
  stagesCompleted: "12 / 12",
  duration: "62 min",
};

const fallbackFindings: DashboardFinding[] = [
  {
    id: "CVE-SIM-001",
    title: "Hardcoded DLMS Authentication Key",
    severity: "critical",
    stage: "Secret Detection",
    tool: "trufflehog",
  },
  {
    id: "CVE-SIM-002",
    title: "Weak AES-128 ECB Mode in Meter Firmware",
    severity: "high",
    stage: "Cryptographic Analysis",
    tool: "entropy",
  },
  {
    id: "CVE-SIM-003",
    title: "Buffer Overflow in DLMS Request Parser",
    severity: "critical",
    stage: "Symbolic Execution",
    tool: "angr",
  },
  {
    id: "CVE-SIM-004",
    title: "Unauthenticated OBIS Code Access",
    severity: "high",
    stage: "Protocol Analysis",
    tool: "wireshark",
  },
  {
    id: "CVE-SIM-005",
    title: "Stack Canary Bypass via Format String",
    severity: "medium",
    stage: "Fuzzing",
    tool: "afl",
  },
];

const fallbackPipeline: DashboardPipeline = {
  vulnerabilities: [
    { name: "Extraction", issues: 0 },
    { name: "Static", issues: 2 },
    { name: "RE", issues: 5 },
    { name: "Secrets", issues: 3 },
    { name: "Crypto", issues: 7 },
    { name: "Protocol", issues: 4 },
    { name: "Symbolic", issues: 8 },
    { name: "Fuzzing", issues: 11 },
  ],
  timeline: [
    { stage: "Upload", mins: 0.5 },
    { stage: "ID", mins: 1.2 },
    { stage: "Extract", mins: 2.8 },
    { stage: "Static", mins: 4.5 },
    { stage: "RE", mins: 8.2 },
    { stage: "Secrets", mins: 2.1 },
    { stage: "Crypto", mins: 3.4 },
    { stage: "Protocol", mins: 5.0 },
    { stage: "Symbolic", mins: 12.0 },
    { stage: "Fuzzing", mins: 18.5 },
    { stage: "Risk", mins: 1.8 },
    { stage: "Report", mins: 0.8 },
  ],
  severity: [
    { name: "Critical", value: 4, fill: "#ef4444" },
    { name: "High", value: 9, fill: "#f97316" },
    { name: "Medium", value: 14, fill: "#f59e0b" },
    { name: "Low", value: 8, fill: "#22c55e" },
  ],
};

const buildDashboardData = (payload?: Partial<DashboardData> | null): DashboardData => ({
  summary: { ...fallbackSummary, ...(payload?.summary ?? {}) },
  metrics: { ...fallbackMetrics, ...(payload?.metrics ?? {}) },
  findings: Array.isArray(payload?.findings) && payload?.findings?.length
    ? payload.findings.map((item) => ({
        id: item?.id ?? undefined,
        title: item?.title ?? undefined,
        severity: item?.severity ?? undefined,
        stage: item?.stage ?? undefined,
        tool: item?.tool ?? undefined,
      }))
    : fallbackFindings,
  pipeline: {
    vulnerabilities: Array.isArray(payload?.pipeline?.vulnerabilities) && payload.pipeline.vulnerabilities.length
      ? payload.pipeline.vulnerabilities
      : fallbackPipeline.vulnerabilities,
    timeline: Array.isArray(payload?.pipeline?.timeline) && payload.pipeline.timeline.length
      ? payload.pipeline.timeline
      : fallbackPipeline.timeline,
    severity: Array.isArray(payload?.pipeline?.severity) && payload.pipeline.severity.length
      ? payload.pipeline.severity
      : fallbackPipeline.severity,
  },
  logs: Array.isArray(payload?.logs) ? payload.logs : [],
});

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border-dim)",
          borderRadius: "var(--radius-sm)",
          padding: "10px 14px",
          fontSize: 12,
        }}
      >
        <div style={{ color: "var(--text-secondary)", marginBottom: 4 }}>{label}</div>
        <div style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>
          {payload[0].value} issues
        </div>
      </div>
    );
  }
  return null;
};

export const Dashboard: React.FC = () => {
  const { activeProject } = useProjectStore();
  const [dashboardData, setDashboardData] = useState<DashboardData>(() => buildDashboardData());

  useEffect(() => {
    let isMounted = true;
    const fetchDashboard = async () => {
        if (!activeProject) return;
        try {
            const res = await api.get(`/projects/${activeProject.id}/dashboard`);
            if (isMounted) {
                setDashboardData(buildDashboardData(res.data));
            }
        } catch(e) {
            console.error(e);
        }
    };
    
    fetchDashboard();
    
    return () => {
      isMounted = false;
    };
  }, [activeProject]);

  const summary = dashboardData.summary ?? {};
  const metrics = dashboardData.metrics ?? {};
  const findings = dashboardData.findings ?? [];
  const pipeline = dashboardData.pipeline ?? {};

  const vulnData = (pipeline?.vulnerabilities ?? []).map((item) => ({
    name: item?.name ?? "",
    issues: item?.issues ?? 0,
  }));

  const severityData = (pipeline?.severity ?? []).map((item) => ({
    name: item?.name ?? "",
    value: item?.value ?? 0,
    fill: item?.fill ?? "#22c55e",
  }));

  const timelineData = (pipeline?.timeline ?? []).map((item) => ({
    stage: item?.stage ?? "",
    mins: item?.mins ?? 0,
  }));

  const totalFindings = metrics?.totalFindings ?? ((summary?.critical ?? 0) + (summary?.high ?? 0) + (summary?.medium ?? 0) + (summary?.low ?? 0));
  const criticalIssues = metrics?.criticalIssues ?? summary?.critical ?? 0;
  const stagesCompleted = metrics?.stagesCompleted ?? "12 / 12";
  const duration = metrics?.duration ?? "62 min";
  const riskScore = summary?.riskScore ?? 32;
  const riskLabel = summary?.riskLabel ?? "CRITICAL RISK";
  const riskSummary = summary?.riskSummary ?? "Firmware poses significant security risk. 4 critical vulnerabilities must be patched before deployment.";
  const findingsCount = findings?.length ?? 0;


  const statCards = [
    {
      icon: <ShieldAlert size={18} />,
      label: "Total Findings",
      value: String(totalFindings),
      sub: "Across 12 pipeline stages",
      color: "var(--accent-red)",
      bg: "rgba(239,68,68,0.1)",
    },
    {
      icon: <AlertTriangle size={18} />,
      label: "Critical Issues",
      value: String(criticalIssues),
      sub: "Require immediate action",
      color: "#f97316",
      bg: "rgba(249,115,22,0.1)",
    },
    {
      icon: <CheckCircle size={18} />,
      label: "Stages Completed",
      value: stagesCompleted,
      sub: "Full pipeline coverage",
      color: "var(--accent-green)",
      bg: "rgba(34,197,94,0.1)",
    },
    {
      icon: <Clock size={18} />,
      label: "Analysis Duration",
      value: duration,
      sub: "Simulated execution time",
      color: "var(--accent-cyan)",
      bg: "rgba(34,211,238,0.1)",
    },
  ];

  return (
    <div className="animate-fade-in">
      {/* Page Header */}
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: "var(--radius-md)",
              background: "rgba(99,120,255,0.15)",
              border: "1px solid rgba(99,120,255,0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--accent-blue)",
            }}
          >
            <Activity size={20} />
          </div>
          <div>
            <h1 className="page-title">Analysis Dashboard</h1>
            <p className="page-subtitle">
              Firmware security overview — DLMS/COSEM Smart Meter · Simulated Run
            </p>
          </div>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        {statCards.map((s, i) => (
          <div key={i} className="card" style={{ padding: 20 }}>
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 14 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "var(--radius-sm)",
                  background: s.bg,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: s.color,
                }}
              >
                {s.icon}
              </div>
            </div>
            <div style={{ fontSize: 26, fontWeight: 800, color: s.color, lineHeight: 1 }}>
              {s.value}
            </div>
            <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)", marginTop: 6 }}>
              {s.label}
            </div>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
              {s.sub}
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Vulnerability by Stage */}
        <div className="card">
          <div className="card-title">
            <TrendingUp size={14} />
            Vulnerabilities by Pipeline Stage
          </div>
          <div style={{ height: 200, marginTop: 16 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={vulnData}>
                <defs>
                  <linearGradient id="vulnGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6378ff" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6378ff" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="issues"
                  stroke="#6378ff"
                  strokeWidth={2}
                  fill="url(#vulnGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Analysis Timeline */}
        <div className="card">
          <div className="card-title">
            <Clock size={14} />
            Stage Analysis Time (minutes)
          </div>
          <div style={{ height: 200, marginTop: 16 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timelineData}>
                <defs>
                  <linearGradient id="timeGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.9} />
                    <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.3} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="stage" tick={{ fontSize: 9 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border-dim)",
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="mins" fill="url(#timeGrad)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid-2">
        {/* Findings Table */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid var(--border-subtle)",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <FileSearch size={15} color="var(--text-muted)" />
            <span className="card-title" style={{ margin: 0 }}>
              Critical Findings
            </span>
            <span className="badge badge-failed" style={{ marginLeft: "auto" }}>
              {findingsCount} Findings
            </span>
          </div>
          <div style={{ overflow: "hidden" }}>
            {findings.map((f, i) => {
              const severity = f?.severity?.toLowerCase() ?? "medium";
              const severityClass = severity === "critical" ? "failed" : severity === "high" ? "running" : "queued";

              return (
                <div
                  key={f?.id ?? `${i}`}
                  style={{
                    padding: "12px 20px",
                    borderBottom:
                      i < findings.length - 1
                        ? "1px solid var(--border-subtle)"
                        : "none",
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 12,
                  }}
                >
                  <span
                    className={`badge badge-${severityClass}`}
                    style={{ flexShrink: 0, fontSize: 10 }}
                  >
                    {severity.toUpperCase()}
                  </span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: "var(--text-primary)",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {f?.title ?? "Unnamed finding"}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                      {f?.stage ?? "Pipeline"} · {f?.tool ?? "simulated"}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Severity Radial + Security Score */}
        <div className="card">
          <div className="card-title">
            <Cpu size={14} />
            Severity Distribution
          </div>
          <div style={{ height: 160, marginTop: 8 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="30%"
                outerRadius="90%"
                data={severityData}
                startAngle={180}
                endAngle={0}
              >
                <RadialBar dataKey="value" cornerRadius={4} />
                <Tooltip
                  contentStyle={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border-dim)",
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
            {severityData.map((s) => (
              <div key={s.name} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: s.fill,
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                  {s.name}: <strong style={{ color: "var(--text-primary)" }}>{s.value}</strong>
                </span>
              </div>
            ))}
          </div>

          <div className="divider" />

          {/* Security Score */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                border: "3px solid #ef4444",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <div>
                <div style={{ fontSize: 20, fontWeight: 800, color: "#ef4444", textAlign: "center", lineHeight: 1 }}>
                  {riskScore}
                </div>
                <div style={{ fontSize: 9, color: "var(--text-muted)", textAlign: "center" }}>
                  /100
                </div>
              </div>
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#ef4444" }}>
                {riskLabel}
              </div>
              <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 3 }}>
                {riskSummary}
              </div>
            </div>
          </div>

          {/* CVSS Bars */}
          <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { label: "Confidentiality Impact", pct: 85, color: "#ef4444" },
              { label: "Integrity Impact", pct: 72, color: "#f97316" },
              { label: "Availability Impact", pct: 60, color: "#f59e0b" },
            ].map((m) => (
              <div key={m.label}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: 11,
                    color: "var(--text-secondary)",
                    marginBottom: 4,
                  }}
                >
                  <span>{m.label}</span>
                  <span style={{ color: m.color, fontWeight: 600 }}>{m.pct}%</span>
                </div>
                <div className="progress-track">
                  <div
                    className="progress-bar"
                    style={{
                      width: `${m.pct}%`,
                      background: `linear-gradient(90deg, ${m.color}, ${m.color}88)`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div
        style={{
          marginTop: 20,
          padding: "14px 20px",
          background: "rgba(99,120,255,0.06)",
          border: "1px solid rgba(99,120,255,0.2)",
          borderRadius: "var(--radius-md)",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <Zap size={16} color="var(--accent-blue)" />
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          <strong style={{ color: "var(--accent-blue)" }}>Live Mode:</strong>{" "}
          All findings and metrics are pre-recorded digital twin outputs based on realistic DLMS/COSEM firmware vulnerability scenarios. Start the Pipeline Simulator to run the full analysis workflow.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
