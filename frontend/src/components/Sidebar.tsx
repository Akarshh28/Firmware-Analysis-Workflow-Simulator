"use client";

import api from "../services/api";
import { ThemeToggle } from "./ThemeToggle";

import React, { useState } from "react";
import {
  LayoutDashboard,
  GitBranch,
  Wrench,
  BookOpen,
  ScrollText,
  Shield,
  Activity,
  ChevronRight,
  Cpu,
  AlertTriangle,
} from "lucide-react";

export type PageId =
  | "upload"
  | "dashboard"
  | "pipeline"
  | "tools"
  | "knowledge"
  | "logs"
  | "reports";

interface SidebarProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
}

const NAV_ITEMS: {
  id: PageId;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  section?: string;
}[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: <LayoutDashboard size={16} />,
    section: "Overview",
  },
  {
    id: "pipeline",
    label: "Pipeline Simulator",
    icon: <GitBranch size={16} />,
    badge: "12 Stages",
    section: "Analysis",
  },
  {
    id: "tools",
    label: "Tool Explorer",
    icon: <Wrench size={16} />,
    section: "Analysis",
  },
  {
    id: "knowledge",
    label: "Knowledge Base",
    icon: <BookOpen size={16} />,
    section: "Resources",
  },
  {
    id: "logs",
    label: "Execution Logs",
    icon: <ScrollText size={16} />,
    section: "Resources",
  },
  {
    id: "reports",
    label: "Reports & Findings",
    icon: <Shield size={16} />,
    section: "Resources",
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onNavigate }) => {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  React.useEffect(() => {
    const checkHealth = () => {
        api.get("/health")
          .then(() => setBackendOnline(true))
          .catch(() => setBackendOnline(false));
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const sections = Array.from(
    new Set(NAV_ITEMS.map((item) => item.section))
  );

  return (
    <nav className="app-sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div className="sidebar-brand-logo">
            <Cpu size={20} />
          </div>
          <div className="sidebar-brand-text">
            <h1>FAWS</h1>
            <p>Firmware Analysis Simulator</p>
          </div>
        </div>
        {/* Project badge */}
        <div
          style={{
            marginTop: 12,
            padding: "6px 10px",
            background: "rgba(99,120,255,0.08)",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <div
            style={{
              fontSize: 10,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            C3iHub · IIT Kanpur
          </div>
          <div
            style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}
          >
            DLMS/COSEM Smart Meter
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div style={{ flex: 1, overflow: "hidden auto", padding: "8px 0" }}>
        {sections.map((section) => (
          <div key={section} className="sidebar-section">
            <div className="sidebar-section-label">{section}</div>
            {NAV_ITEMS.filter((item) => item.section === section).map(
              (item) => (
                <button
                  key={item.id}
                  className={`sidebar-nav-item ${activePage === item.id ? "active" : ""}`}
                  onClick={() => onNavigate(item.id)}
                >
                  {item.icon}
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
                  {activePage === item.id && (
                    <ChevronRight
                      size={12}
                      style={{ marginLeft: "auto", opacity: 0.6 }}
                    />
                  )}
                </button>
              )
            )}
          </div>
        ))}
      </div>

      {/* Footer / Status */}
      <div className="sidebar-footer">
        {/* Backend Status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "8px 10px",
            background:
              backendOnline === true
                ? "rgba(34,197,94,0.08)"
                : backendOnline === false
                ? "rgba(239,68,68,0.08)"
                : "rgba(99,120,255,0.06)",
            border: `1px solid ${
              backendOnline === true
                ? "rgba(34,197,94,0.2)"
                : backendOnline === false
                ? "rgba(239,68,68,0.2)"
                : "var(--border-subtle)"
            }`,
            borderRadius: "var(--radius-sm)",
            marginBottom: 8,
          }}
        >
          <div
            className={`status-dot ${
              backendOnline === true
                ? "status-dot-success"
                : backendOnline === false
                ? "status-dot-failed"
                : "status-dot-queued"
            }`}
            style={
              backendOnline === null
                ? { animation: "pulse-amber 1.5s infinite" }
                : {}
            }
          />
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-primary)" }}>
              {backendOnline === true
                ? "API Server Online"
                : backendOnline === false
                ? "API Server Offline"
                : "Checking API…"}
            </div>
            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
              127.0.0.1:8000
            </div>
          </div>
          {backendOnline === false && (
            <AlertTriangle size={12} style={{ marginLeft: "auto", color: "var(--accent-red)" }} />
          )}
        </div>

        {/* Theme Switcher */}
        <div style={{ marginBottom: 12 }}>
          <ThemeToggle />
        </div>

        {/* Sim Mode */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            fontSize: 11,
            color: "var(--text-muted)",
          }}
        >
          <Activity size={12} />
          <span>Simulation Mode Active</span>
        </div>
        <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
          v1.0.0 · Digital Twin Pipeline
        </div>
      </div>
    </nav>
  );
};
