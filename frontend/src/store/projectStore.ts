import { create } from "zustand";
import type {
  Project,
  PipelineSession,
  LogEntry,
  ToolDetails,
} from "../Types/project";

const API_BASE = "http://localhost:8000/api";

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
    file: File
  ) => Promise<void>;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  activeProject: null,
  activePipeline: null,
  logs: [],
  tools: [],
  isLoading: false,

  fetchProjects: async () => {
    set({ isLoading: true });

    try {
      const res = await fetch(`${API_BASE}/projects`);

      if (res.ok) {
        const data = await res.json();

        set({ projects: data });

        if (data.length > 0 && !get().activeProject) {
          get().selectProject(data[0]);
        }
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
    const res = await fetch(`${API_BASE}/projects`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name,
        description,
        target_architecture: targetArch,
      }),
    });

    if (!res.ok) {
      throw new Error("Project creation failed");
    }

    const project = await res.json();

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
      const res = await fetch(
        `${API_BASE}/projects/${projectId}/pipeline`
      );

      if (res.ok) {
        set({
          activePipeline: await res.json(),
        });
      }
    } catch (e) {
      console.error(e);
    }
  },

  startPipeline: async (projectId) => {
    await fetch(
      `${API_BASE}/projects/${projectId}/pipeline/run`,
      {
        method: "POST",
      }
    );

    await get().fetchPipelineStatus(projectId);
  },

  stopPipeline: async (projectId) => {
    await fetch(
      `${API_BASE}/projects/${projectId}/pipeline/stop`,
      {
        method: "POST",
      }
    );

    await get().fetchPipelineStatus(projectId);
  },

  fetchLogs: async (projectId) => {
    try {
      const res = await fetch(
        `${API_BASE}/projects/${projectId}/logs`
      );

      if (res.ok) {
        set({
          logs: await res.json(),
        });
      }
    } catch (e) {
      console.error(e);
    }
  },

  fetchTools: async () => {
    try {
      const res = await fetch(`${API_BASE}/tools`);

      if (res.ok) {
        set({
          tools: await res.json(),
        });
      }
    } catch (e) {
      console.error(e);
    }
  },

  uploadFirmware: async (
    projectId: number,
    file: File
  ) => {
    const formData = new FormData();

    formData.append("firmware", file);

    const res = await fetch(
      `${API_BASE}/projects/${projectId}/upload`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!res.ok) {
      throw new Error("Firmware upload failed");
    }
  },
}));