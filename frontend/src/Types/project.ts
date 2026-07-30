export interface Project {
  id: number;
  name: string;
  description?: string;
  target_architecture: string;
  status: string;
  firmware_filepath?: string | null;
  file_size?: number | null;
  checksum?: string | null;
  created_at: string;
}

export interface PipelineStage {
  stage: string;
  tool: string;
  description: string;
  status: string;
  exit_code: number | null;
  progress?: number;
}

export interface PipelineSession {
  session_id: number;
  status: string;
  current_stage: string;
  stages: PipelineStage[];
}

export interface LogEntry {
  id: number;
  tool_name: string;
  log_type: string;
  message: string;
  timestamp: string;
}

export interface ToolDetails {
  name: string;
  version: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  docs: any;
}