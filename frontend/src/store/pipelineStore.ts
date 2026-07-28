import { create } from "zustand";
import { defaultPipeline } from "../data/defaultPipeline";

type Status =
  | "idle"
  | "queued"
  | "running"
  | "completed"
  | "failed";

interface PipelineStore {
  pipeline: typeof defaultPipeline;

  resetPipeline: () => void;

  updateNodeStatus: (
    nodeId: string,
    status: Status,
    progress?: number
  ) => void;

  simulatePipeline: () => Promise<void>;
}

export const usePipelineStore = create<PipelineStore>((set, get) => ({

  pipeline: defaultPipeline,

  resetPipeline: () =>
    set({
      pipeline: JSON.parse(JSON.stringify(defaultPipeline)),
    }),

  updateNodeStatus: (nodeId, status, progress = 0) =>
    set((state) => ({
      pipeline: {
        ...state.pipeline,
        nodes: state.pipeline.nodes.map((node) =>
          node.id === nodeId
            ? { ...node, status, progress }
            : node
        ),
      },
    })),

  simulatePipeline: async () => {

    const nodes = get().pipeline.nodes;

    for (const node of nodes) {

      get().updateNodeStatus(node.id, "running", 0);

      for (let i = 0; i <= 100; i += 10) {

        await new Promise((r) => setTimeout(r, 200));

        get().updateNodeStatus(node.id, "running", i);

      }

      get().updateNodeStatus(node.id, "completed", 100);

    }

  },

}));