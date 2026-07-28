export interface Project {
  id: number;
  name: string;
  description?: string;
  target_architecture: string;
  status: string;
  firmware_filepath?: string | null;
  created_at: string;
}

export interface PipelineSession {
  session_id: number;
  status: string;
  current_stage: string;

  stages: {
    stage: string;
    tool: string;
    description: string;
    status: string;
    exit_code: number | null;
  }[];
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
  docs: any;
}