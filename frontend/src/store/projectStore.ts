import { create } from "zustand";
import type {
  Project,
  PipelineSession,
  LogEntry,
  ToolDetails,
} from "../Types/project";

import api from "../services/api";



interface ProjectState {
  projects: Project[];
  activeProject: Project | null;
  activePipeline: PipelineSession | null;
  logs: LogEntry[];
  tools: ToolDetails[];
  isLoading: boolean;

  fetchProjects: () => Promise<void>;
  createProject: (
    name: string,
    description: string,
    targetArch: string
  ) => Promise<Project>;

  selectProject: (project: Project) => void;

  fetchPipelineStatus: (projectId: number) => Promise<void>;

  startPipeline: (projectId: number) => Promise<void>;

  stopPipeline: (projectId: number) => Promise<void>;

  fetchLogs: (projectId: number) => Promise<void>;

  fetchTools: () => Promise<void>;

  uploadFirmware: (
    projectId: number,
    file: File,
    onProgress?: (progress: number) => void
  ) => Promise<void>;
  
  addLog: (log: LogEntry) => void;
  updateActivePipelineStatus: (status: string) => void;
  clearActiveProject: () => void;
  
  toolExplorerState: { toolName: string | null; activeTab: 'overview' | 'commands' | 'console' | 'troubleshoot' };
  setToolExplorerState: (toolName: string, activeTab: 'overview' | 'commands' | 'console' | 'troubleshoot') => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  activeProject: null,
  activePipeline: null,
  logs: [],
  tools: [],
  isLoading: false,
  
  toolExplorerState: { toolName: null, activeTab: 'overview' },
  setToolExplorerState: (toolName, activeTab) => set({ toolExplorerState: { toolName, activeTab } }),
  
  addLog: (log) => set((state) => ({ logs: [...state.logs, log] })),
  
  updateActivePipelineStatus: (status) => set((state) => ({
    activePipeline: state.activePipeline ? { ...state.activePipeline, status } : null
  })),

  clearActiveProject: () => {
    set({
      activeProject: null,
      activePipeline: null,
      logs: [],
    });
  },

  fetchProjects: async () => {
    set({ isLoading: true });
    try {
      const res = await api.get(`projects`);
      set({ projects: res.data });
      if (res.data.length > 0 && !get().activeProject) {
        get().selectProject(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      set({ isLoading: false });
    }
  },

  createProject: async (
    name,
    description,
    targetArch
  ) => {
    const res = await api.post(`projects`, {
        name,
        description,
        target_architecture: targetArch,
    });
    
    const project = res.data;
    await get().fetchProjects();
    get().selectProject(project);

    return project;
  },

  selectProject: (project) => {
    set({
      activeProject: project,
      activePipeline: null,
      logs: [],
    });

    get().fetchPipelineStatus(project.id);

    get().fetchLogs(project.id);
  },

  fetchPipelineStatus: async (projectId) => {
    try {
      const res = await api.get(`projects/${projectId}/pipeline`);
      set({
        activePipeline: res.data,
      });
    } catch (e) {
      console.error(e);
    }
  },

  startPipeline: async (projectId) => {
    await api.post(`projects/${projectId}/pipeline/run`);
    await get().fetchPipelineStatus(projectId);
  },

  stopPipeline: async (projectId) => {
    await api.post(`projects/${projectId}/pipeline/stop`);
    await get().fetchPipelineStatus(projectId);
  },

  fetchLogs: async (projectId) => {
    try {
      const res = await api.get(`projects/${projectId}/logs`);
      set({
        logs: res.data,
      });
    } catch (e) {
      console.error(e);
    }
  },

  fetchTools: async () => {
    try {
      const res = await api.get(`tools`);
      set({
        tools: res.data,
      });
    } catch (e) {
      console.error(e);
    }
  },

  uploadFirmware: async (
    projectId: number,
    file: File,
    onProgress?: (progress: number) => void
  ) => {
    const formData = new FormData();
    formData.append("firmware", file);

    const res = await api.post(`projects/${projectId}/upload`, formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
    
    // Update active project with the new details
    set((state) => {
        if (state.activeProject && state.activeProject.id === projectId) {
            return {
                activeProject: {
                    ...state.activeProject,
                    checksum: res.data.checksum,
                    file_size: res.data.filesize,
                    firmware_filepath: res.data.filepath
                }
            };
        }
        return state;
    });
  },
}));