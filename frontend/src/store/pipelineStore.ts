import { create } from "zustand";
import api from "../services/api";
import { defaultPipeline } from "../data/defaultPipeline";
import { useProjectStore } from "./projectStore";

type Status =
  | "idle"
  | "queued"
  | "running"
  | "completed"
  | "failed";

interface PipelineStore {
  pipeline: typeof defaultPipeline;
  loading: boolean;

  resetPipeline: () => void;
  resetPipelineBackend: (projectId: number) => Promise<void>;

  fetchPipeline: (projectId: number) => Promise<void>;

  runPipeline: (projectId: number) => Promise<void>;

  connectWebSocket: (projectId: number) => void;
  disconnectWebSocket: () => void;
  socket: WebSocket | null;
}

export const usePipelineStore = create<PipelineStore>((set, get) => ({
  pipeline: defaultPipeline,
  loading: false,
  socket: null,

  resetPipeline: () =>
    set({
      pipeline: JSON.parse(JSON.stringify(defaultPipeline)),
    }),
    
  resetPipelineBackend: async (projectId) => {
    try {
        await api.post(`projects/${projectId}/pipeline/stop`);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
        // ignore if not running
    }
    try {
        await api.post(`projects/${projectId}/pipeline/reset`);
        get().resetPipeline();
        await get().fetchPipeline(projectId);
        useProjectStore.getState().selectProject(useProjectStore.getState().activeProject!);
    } catch (e) {
        console.error(e);
    }
  },

  fetchPipeline: async (projectId) => {
    try {
      const res = await api.get(`projects/${projectId}/pipeline`);

      const backendStages = res.data.stages;

      set((state) => ({
        pipeline: {
          ...state.pipeline,
          nodes: state.pipeline.nodes.map((node) => {
            const stage = backendStages.find(
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              (s: any) => s.tool === node.toolName
            );

            if (!stage) return node;

            let status: Status = "idle";

            switch (stage.status) {
              case "running":
                status = "running";
                break;

              case "success":
                status = "completed";
                break;

              case "failed":
                status = "failed";
                break;

              default:
                status = "idle";
            }

            return {
              ...node,
              status,
              progress:
                status === "completed"
                  ? 100
                  : status === "running"
                  ? 50
                  : 0,
            };
          }),
        },
      }));
    } catch (e) {
      console.error(e);
    }
  },

  runPipeline: async (projectId) => {
    try {
      await api.post(`projects/${projectId}/pipeline/run`);
      await get().fetchPipeline(projectId);
    } catch (e) {
      console.error(e);
    }
  },

  connectWebSocket: (projectId) => {
    let apiUrl = process.env.NODE_ENV === 'production' 
                   ? "https://firmware-analysis-workflow-simulator.onrender.com/api/" 
                   : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/");
    
    apiUrl = apiUrl.replace(/\/+$/, '');
    if (!apiUrl.endsWith('/api')) {
        apiUrl += '/api';
    }
    apiUrl += '/';
    const wsUrl = apiUrl.replace(/^http/, 'ws').replace(/\/api\/$/, '');
    const ws = new WebSocket(`${wsUrl}/api/ws/${projectId}`);
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === "STATUS_UPDATE" || message.type === "PROGRESS_TICK") {
        set((state) => ({
          pipeline: {
            ...state.pipeline,
            nodes: state.pipeline.nodes.map((node) => {
              if (node.toolName === message.data.tool_name || node.toolName === message.data.current_tool) {
                return {
                  ...node,
                  status: message.data.status || node.status,
                  progress: message.data.progress !== undefined ? message.data.progress : node.progress
                };
              }
              return node;
            })
          }
        }));
      } else if (message.type === "TOOL_SUCCESS") {
        set((state) => ({
          pipeline: {
            ...state.pipeline,
            nodes: state.pipeline.nodes.map((node) => {
              if (node.toolName === message.data.tool_name) {
                return { ...node, status: "completed", progress: 100 };
              }
              return node;
            })
          }
        }));
      } else if (message.type === "PIPELINE_STATUS") {
        // Handle global pipeline status changes
        if (message.data.status === "READY") {
            get().resetPipeline();
        }
        useProjectStore.getState().updateActivePipelineStatus(message.data.status);
      } else if (message.type === "LOG_NEW") {
        useProjectStore.getState().addLog(message.data);
      }
    };

    set({ socket: ws });
  },

  disconnectWebSocket: () => {
    const { socket } = get();
    if (socket) {
      socket.close();
      set({ socket: null });
    }
  }
}));
