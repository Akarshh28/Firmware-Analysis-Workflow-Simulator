"use client";

import React, { useState } from "react";
import { Sidebar, PageId } from "../components/Sidebar";
import { Dashboard } from "../pages/Dashboard";
import { PipelineSimulator } from "../pages/PipelineSimulator";
import { ToolExplorer } from "../pages/ToolExplorer";
import { KnowledgeBase } from "../pages/KnowledgeBase";
import { Logs } from "../pages/Logs";
import { Reports } from "../pages/Reports";
import {
  LayoutDashboard,
  GitBranch,
  Wrench,
  BookOpen,
  ScrollText,
  Shield,
  BellRing,
  Settings,
} from "lucide-react";

const PAGE_ICONS: Record<PageId, React.ReactNode> = {
  dashboard: <LayoutDashboard size={14} />,
  pipeline:  <GitBranch size={14} />,
  tools:     <Wrench size={14} />,
  knowledge: <BookOpen size={14} />,
  logs:      <ScrollText size={14} />,
  reports:   <Shield size={14} />,
};

const PAGE_TITLES: Record<PageId, string> = {
  dashboard: "Dashboard",
  pipeline:  "Pipeline Simulator",
  tools:     "Tool Explorer",
  knowledge: "Knowledge Base",
  logs:      "Execution Logs",
  reports:   "Reports & Findings",
};

export default function Home() {
  const [activePage, setActivePage] = useState<PageId>("dashboard");

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      {/* Main */}
      <main className="app-main">
        {/* Header Bar */}
        <header className="app-header">
          {/* Breadcrumb */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "var(--text-muted)", fontSize: 13 }}>FAWS</span>
            <span style={{ color: "var(--text-muted)" }}>/</span>
            <span style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-primary)", fontSize: 13, fontWeight: 600 }}>
              {PAGE_ICONS[activePage]}
              {PAGE_TITLES[activePage]}
            </span>
          </div>

          {/* Spacer */}
          <div style={{ flex: 1 }} />

          {/* Top right actions */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* Sim Mode Badge */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "5px 12px",
                background: "rgba(245,158,11,0.1)",
                border: "1px solid rgba(245,158,11,0.25)",
                borderRadius: 99,
                fontSize: 11,
                fontWeight: 600,
                color: "var(--accent-amber)",
              }}
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: "var(--accent-amber)",
                  animation: "pulse-amber 1.5s ease infinite",
                }}
              />
              SIMULATION MODE
            </div>

            <button
              className="btn btn-secondary btn-icon"
              title="Notifications"
              style={{ padding: 7 }}
            >
              <BellRing size={15} />
            </button>

            <button
              className="btn btn-secondary btn-icon"
              title="Settings"
              style={{ padding: 7 }}
            >
              <Settings size={15} />
            </button>

            {/* Avatar */}
            <div
              style={{
                width: 30,
                height: 30,
                borderRadius: "50%",
                background: "var(--gradient-brand)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 11,
                fontWeight: 800,
                color: "#fff",
                cursor: "pointer",
              }}
              title="C3iHub Researcher"
            >
              R
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="app-content">
          {activePage === "dashboard" && <Dashboard />}
          {activePage === "pipeline"  && <PipelineSimulator />}
          {activePage === "tools"     && <ToolExplorer />}
          {activePage === "knowledge" && <KnowledgeBase />}
          {activePage === "logs"      && <Logs />}
          {activePage === "reports"   && <Reports />}
        </div>
      </main>
    </div>
  );
}