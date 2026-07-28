export type NodeStatus =
  | "idle"
  | "queued"
  | "running"
  | "completed"
  | "failed";

export interface PipelineNode {

  id: string;

  toolName: string;

  status: NodeStatus;

  progress: number;

  startedAt?: string;

  finishedAt?: string;

}

export interface PipelineEdge{

  from:string;

  to:string;

}

export interface Pipeline{

  id:string;

  name:string;

  nodes:PipelineNode[];

  edges:PipelineEdge[];

}