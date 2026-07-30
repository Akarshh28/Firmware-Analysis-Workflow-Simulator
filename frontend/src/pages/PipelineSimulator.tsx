import { useEffect, useState, useRef } from "react";
import { usePipelineStore } from "../store/pipelineStore";
import { useProjectStore } from "../store/projectStore";
import { useNotificationStore } from "../store/notificationStore";
import { Upload } from "./Upload";
import { PageId } from "../components/Sidebar";

export default function PipelineSimulator({ onNavigate }: { onNavigate?: (page: PageId) => void }) {
  const {

    pipeline,
    fetchPipeline,
    runPipeline,
    resetPipelineBackend,
  } = usePipelineStore();

  const { activeProject, activePipeline, clearActiveProject } = useProjectStore();

  const [running, setRunning] = useState(false);
  const prevStatusRef = useRef<string | undefined>(activePipeline?.status);

  useEffect(() => {
    if (activeProject) {
        fetchPipeline(activeProject.id);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProject]);

  // Navigate to Reports ONLY when pipeline transitions to COMPLETED
  useEffect(() => {
    const currentStatus = activePipeline?.status;
    const prevStatus = prevStatusRef.current;
    
    if (currentStatus === "COMPLETED" && prevStatus === "RUNNING") {
      useNotificationStore.getState().addNotification({
        title: "Analysis Complete",
        message: "Firmware analysis pipeline has successfully finished.",
        type: "success",
        action: { label: "View Report", pageId: "reports" }
      });

      if (onNavigate) {
        // Small delay for better UX so user sees the "Completed" state briefly
        const t = setTimeout(() => {
          onNavigate("reports");
        }, 1500);
        
        prevStatusRef.current = currentStatus;
        return () => clearTimeout(t);
      }
    } else if (currentStatus === "FAILED" && prevStatus === "RUNNING") {
      useNotificationStore.getState().addNotification({
        title: "Analysis Failed",
        message: "The firmware analysis pipeline encountered an error.",
        type: "error",
        action: { label: "Open Simulator", pageId: "pipeline" }
      });
    }
    
    prevStatusRef.current = currentStatus;
  }, [activePipeline?.status, onNavigate]);

  const handleRun = async () => {
    if (!activeProject) return;
    setRunning(true);
    await resetPipelineBackend(activeProject.id);
    await runPipeline(activeProject.id);
    setRunning(false);
  };

  const canRun = !!activeProject && activePipeline?.status !== "WAITING_UPLOAD" && activePipeline?.status !== "RUNNING" && !running;

  return (
    <div
      className="p-6 rounded-xl"
      style={{
        background: "var(--bg-card)",
        color: "var(--text-primary)",
      }}
    >
      <div className="flex gap-3 mb-6">
        <button
          onClick={handleRun}
          disabled={!canRun}
          className="px-4 py-2 rounded bg-blue-600 text-white flex items-center gap-2"
          style={{ opacity: canRun ? 1 : 0.5, cursor: canRun ? "pointer" : "not-allowed" }}
        >
          {(running || activePipeline?.status === "RUNNING") && (
            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {running || activePipeline?.status === "RUNNING" ? "Running..." : "Run Pipeline"}
        </button>

        <button
          onClick={() => activeProject && clearActiveProject()}
          className="px-4 py-2 rounded bg-gray-700 text-white hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          disabled={running || !activeProject}
        >
          Reset
        </button>
      </div>
      
      {!running && activePipeline?.status !== "RUNNING" && (
          <div style={{ marginBottom: 20, border: "1px dashed var(--border-subtle)", borderRadius: 10, padding: 10, background: "rgba(0,0,0,0.2)" }}>
              <h3 style={{ marginLeft: 20, marginTop: 10, fontSize: 16, color: "var(--text-muted)" }}>Upload New Firmware</h3>
              <Upload />
          </div>
      )}

      {pipeline.nodes.map((node) => {
        const isRunning = node.status === "running";
        const isCompleted = node.status === "completed";
        const isFailed = node.status === "failed";
        
        return (
            <div
              key={node.id}
              style={{
                border: isRunning ? "1px solid var(--accent-cyan)" : isFailed ? "1px solid var(--accent-red)" : "1px solid var(--border-dim)",
                borderRadius: 10,
                padding: 16,
                marginBottom: 18,
                background: isRunning ? "rgba(99,120,255,0.05)" : "var(--bg-secondary)",
                transition: "all 0.3s ease",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <h3 style={{ fontSize: 18, fontWeight: 700, color: isRunning ? "var(--accent-cyan)" : "var(--text-primary)" }}>
                    {node.stage}
                  </h3>
                  <div style={{
                      padding: "4px 8px", 
                      borderRadius: 4, 
                      fontSize: 12,
                      fontWeight: 600,
                      background: isRunning ? "rgba(99,120,255,0.15)" : isCompleted ? "rgba(34,197,94,0.15)" : isFailed ? "rgba(239,68,68,0.15)" : "rgba(255,255,255,0.05)",
                      color: isRunning ? "var(--accent-cyan)" : isCompleted ? "var(--accent-green)" : isFailed ? "var(--accent-red)" : "var(--text-muted)",
                      textTransform: "uppercase"
                  }}>
                      {node.status}
                  </div>
              </div>

              <div style={{ color: "var(--text-secondary)", marginBottom: 12 }}>
                {node.description}
              </div>

              <div style={{ marginBottom: 16, fontSize: 14 }}>
                <span style={{ color: "var(--text-muted)" }}>Tool:</span> <strong style={{ color: "var(--text-primary)"}}>{node.toolName}</strong>
              </div>

              <div style={{ width: "100%", height: 8, background: "var(--bg-tertiary)", borderRadius: 4, overflow: "hidden" }}>
                  <div style={{ 
                      width: `${node.progress}%`, 
                      height: "100%", 
                      background: isCompleted ? "var(--accent-green)" : isFailed ? "var(--accent-red)" : "var(--accent-cyan)",
                      transition: "width 0.3s ease",
                      position: "relative"
                  }}>
                      {isRunning && (
                          <div style={{
                              position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
                              background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)",
                              animation: "shimmer 1.5s infinite"
                          }} />
                      )}
                  </div>
              </div>
              
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8, fontSize: 12, color: "var(--text-muted)", alignItems: "center" }}>
                  <div>Progress: {node.progress}%</div>
                  {isRunning && <div style={{ color: "var(--accent-cyan)" }}>Running...</div>}
                  {isFailed && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // set global tool explorer state
                        useProjectStore.getState().setToolExplorerState(node.toolName, 'troubleshoot');
                        if (onNavigate) onNavigate("tools");
                      }}
                      style={{
                        padding: "4px 12px",
                        background: "rgba(239,68,68,0.1)",
                        border: "1px solid rgba(239,68,68,0.3)",
                        borderRadius: "4px",
                        color: "var(--accent-red)",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      Troubleshoot
                    </button>
                  )}
              </div>
            </div>
        );
      })}
    </div>
  );
}