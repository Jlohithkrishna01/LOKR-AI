export interface User {
  id: number;
  name: string;
  preferred_name?: string | null;
  email: string;
  profile_image: string | null;
  bio: string | null;
  provider?: string;
  provider_id?: string | null;
  google_id?: string | null;
  apple_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserStats {
  conversation_count: number;
  message_count: number;
}

export interface Source {
  id?: number;
  title: string;
  url: string;
  source_name: string;
  snippet?: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  file_name?: string | null;
  file_url?: string | null;
  file_type?: string | null;
  created_at: string;
  sources?: Source[];
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
  last_message?: string | null;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  enter_to_send: boolean;
  show_timestamps: boolean;
  default_model: string;
  system_prompt: string | null;
}

export interface UploadedFileInfo {
  file_name: string;
  file_url: string;
  file_type: string;
  file_size: number;
  extracted_text: string;
}
