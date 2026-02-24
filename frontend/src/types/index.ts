export interface FileUploadResponse {
  filename: string;
  stored_name: string;
  uri: string;
  message: string;
}

export interface AgentEvent {
  status: 'info' | 'thinking' | 'executing' | 'success' | 'error' | 'complete';
  message: string;
  tool?: string;
  args?: Record<string, any>;
  result?: any;
}

export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  tool_call_id?: string;
}

export interface ArtifactNodeData {
  label: string;
  description?: string;
  type?: string;
  uri?: string;
}
