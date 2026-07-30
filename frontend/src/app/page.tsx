"use client";

import React, { useState } from "react";
import { Sidebar, PageId } from "../components/Sidebar";
import { Dashboard } from "../pages/Dashboard";

import  PipelineSimulator  from "../pages/PipelineSimulator";
import { ToolExplorer } from "../pages/ToolExplorer";
import { KnowledgeBase } from "../pages/KnowledgeBase";
import { Logs } from "../pages/Logs";
import { Reports } from "../pages/Reports";
import { NotificationsDropdown } from "../components/NotificationsDropdown";
import { SettingsModal } from "../components/SettingsModal";
import { UserProfileDropdown } from "../components/UserProfileDropdown";
import {
  LayoutDashboard,
  GitBranch,
  Wrench,
  BookOpen,
  ScrollText,
  Shield,
  Settings,
  Upload as UploadIcon,
} from "lucide-react";

const PAGE_ICONS: Record<PageId, React.ReactNode> = {
  upload:    <UploadIcon size={14} />,
  dashboard: <LayoutDashboard size={14} />,
  pipeline:  <GitBranch size={14} />,
  tools:     <Wrench size={14} />,
  knowledge: <BookOpen size={14} />,
  logs:      <ScrollText size={14} />,
  reports:   <Shield size={14} />,
};

const PAGE_TITLES: Record<PageId, string> = {
  upload:    "Upload Firmware",
  dashboard: "Dashboard",
  pipeline:  "Pipeline Simulator",
  tools:     "Tool Explorer",
  knowledge: "Knowledge Base",
  logs:      "Execution Logs",
  reports:   "Reports & Findings",
};

import { usePipelineStore } from "../store/pipelineStore";
import { useProjectStore } from "../store/projectStore";

export default function Home() {
  const [activePage, setActivePage] = useState<PageId>("dashboard");
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { connectWebSocket, disconnectWebSocket } = usePipelineStore();
  const { fetchProjects, activeProject, activePipeline } = useProjectStore();

  React.useEffect(() => {
    fetchProjects();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  React.useEffect(() => {
    if (activeProject?.id) {
        connectWebSocket(activeProject.id);
    }
    return () => {
      disconnectWebSocket();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProject?.id]);

  let badgeText = "SYSTEM READY";
  let badgeColor = "var(--text-muted)";
  let badgeBg = "rgba(255,255,255,0.05)";
  let badgeBorder = "rgba(255,255,255,0.1)";
  let animation = "none";
  let pulseGlow = "none";

  if (activePipeline?.status === "RUNNING") {
    badgeText = "ANALYZING...";
    badgeColor = "var(--accent-amber)";
    badgeBg = "rgba(245,158,11,0.1)";
    badgeBorder = "rgba(245,158,11,0.25)";
    animation = "pulse-amber 2s ease infinite";
    pulseGlow = "0 0 8px rgba(245,158,11,0.6)";
  } else if (activePipeline?.status === "COMPLETED") {
    badgeText = "FINDINGS READY";
    badgeColor = "var(--accent-green)";
    badgeBg = "rgba(34,197,94,0.1)";
    badgeBorder = "rgba(34,197,94,0.25)";
  } else if (activePipeline?.status === "FAILED") {
    badgeText = "ANALYSIS FAILED";
    badgeColor = "var(--accent-red)";
    badgeBg = "rgba(244,63,94,0.1)";
    badgeBorder = "rgba(244,63,94,0.25)";
  }

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
            {/* Dynamic Status Badge */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "5px 12px",
                background: badgeBg,
                border: `1px solid ${badgeBorder}`,
                borderRadius: 99,
                fontSize: 11,
                fontWeight: 600,
                color: badgeColor,
                userSelect: "none",
                transition: "all 0.3s ease",
              }}
              title="Live Analysis Engine Status"
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: badgeColor,
                  animation: animation,
                  boxShadow: pulseGlow
                }}
              />
              {badgeText}
            </div>

            <NotificationsDropdown onNavigate={(p) => setActivePage(p)} />

            <button
              className="btn btn-secondary btn-icon"
              title="Settings"
              style={{ padding: 7 }}
              onClick={() => setIsSettingsOpen(true)}
            >
              <Settings size={15} />
            </button>

            {/* Avatar */}
            <UserProfileDropdown />
          </div>
        </header>

        {/* Page Content */}
        <div className="content-area">
          {activePage === "dashboard" && <Dashboard />}
          {activePage === "pipeline" && <PipelineSimulator onNavigate={(p) => setActivePage(p)} />}
          {activePage === "tools" && <ToolExplorer />}
          {activePage === "knowledge" && <KnowledgeBase />}
          {activePage === "logs" && <Logs />}
          {activePage === "reports" && <Reports />}
        </div>
      </main>

      {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} />}
    </div>
  );
}