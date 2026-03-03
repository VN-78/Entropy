export interface FileUploadResponse {
  filename: string;
  stored_name: string;
  uri: string;
  message: string;
}

export interface AgentEvent {
  status: 'info' | 'thinking' | 'executing' | 'success' | 'error' | 'complete' | 'user_message' | 'history_update';
  message?: string;
  tool?: string;
  args?: Record<string, any>;
  result?: any;
  messages?: Message[];
}

export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string | null;
  tool_call_id?: string;
  tool_calls?: any[];
}

export interface ArtifactNodeData {
  label: string;
  description?: string;
  type?: string;
  uri?: string;
}
