import {
  User,
  UserStats,
  Conversation,
  ConversationDetail,
  UserSettings,
  UploadedFileInfo,
  Source
} from '../types';

import { extractPreferredName } from '../utils/name';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export const getToken = (): string | null => {
  return localStorage.getItem('lokr_token') || localStorage.getItem('lumiq_token');
};

export const setToken = (token: string): void => {
  localStorage.setItem('lokr_token', token);
};

export const removeToken = (): void => {
  localStorage.removeItem('lokr_token');
  localStorage.removeItem('lumiq_token');
};

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err: any) {
    const isGH = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
    if (isGH) {
      throw new ApiError(
        'Backend server is not running on GitHub Pages (static host). Click "Try Demo Mode" below to explore without a backend!',
        0
      );
    }
    throw new ApiError(
      'Cannot connect to backend server. Please make sure the backend is running on http://127.0.0.1:8000 (run start-all.bat).',
      0
    );
  }

  if (response.status === 401) {
    removeToken();
    const loginPath = `${import.meta.env.BASE_URL}login`;
    if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/signup')) {
      window.location.href = `${loginPath}?expired=true`;
    }
  }

  if (!response.ok) {
    let errorMsg = 'An unexpected error occurred.';
    const isGH = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
    if (response.status === 404 && isGH) {
      errorMsg = 'Backend API is not hosted on GitHub Pages (static hosting). Click "Try Demo Mode" below to explore!';
    } else if (response.status === 404) {
      errorMsg = 'API endpoint not found (404). Please ensure the backend is running.';
    } else {
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorData.message || errorMsg;
      } catch {
        errorMsg = response.statusText || `Request failed (${response.status})`;
      }
    }
    throw new ApiError(errorMsg, response.status);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// -------------------------------------------------------------
// Interactive Demo Mode Support (for GitHub Pages & offline preview)
// -------------------------------------------------------------
const DEMO_STORAGE_KEY = 'lumiq_demo_conversations';
const DEMO_SETTINGS_KEY = 'lumiq_demo_settings';

export function isDemoOrSocialToken(t?: string | null): boolean {
  const token = t !== undefined ? t : getToken();
  return token === 'demo-guest-token';
}

interface DemoConvData {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Array<{
    id: number;
    conversation_id: number;
    role: 'user' | 'assistant';
    content: string;
    file_name?: string | null;
    file_url?: string | null;
    file_type?: string | null;
    created_at: string;
    sources?: Source[];
  }>;
}

function getDemoConversations(): DemoConvData[] {
  try {
    const raw = localStorage.getItem(DEMO_STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}

  const defaultConv: DemoConvData = {
    id: 1,
    title: 'Welcome to LOKR AI 👋',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    messages: [
      {
        id: 101,
        conversation_id: 1,
        role: 'assistant',
        content: `### Welcome to LOKR AI! 🚀\n\nYou are running in **Interactive Demo Mode** directly in your browser on GitHub Pages.\n\nHere are some of the features you can explore:\n- **Real-Time Streaming**: Natural, smooth AI conversation simulation.\n- **Syntax Highlighted Code**: Rich rendering for Python, JavaScript, TypeScript, SQL, and more.\n- **Web Search Citations**: Live source cards and references.\n- **Document Intelligence**: Upload files and query their contents.\n- **Theme Switcher**: Switch between Light, Dark, and System modes using the top-right toggle.\n\nAsk me anything or select a suggestion card below to get started!`,
        created_at: new Date().toISOString(),
        sources: [
          {
            title: 'LOKR AI GitHub Repository',
            url: 'https://github.com/Jlohithkrishna01/Ai_App',
            source_name: 'GitHub',
            snippet: 'Production-grade intelligent AI chatbot inspired by ChatGPT.',
          },
        ],
      },
    ],
  };

  try {
    localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify([defaultConv]));
  } catch {}
  return [defaultConv];
}

function saveDemoConversations(convs: DemoConvData[]) {
  try {
    localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(convs));
  } catch {}
}

export const api = {
  // Authentication
  async signup(data: any): Promise<{ access_token: string; token_type: string; user: User }> {
    return request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async loginWithGoogle(data: { credential?: string; access_token?: string; code?: string }): Promise<{ access_token: string; token_type: string; user: User }> {
    return request('/auth/google', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async loginWithApple(data: { id_token: string; code?: string; user?: any }): Promise<{ access_token: string; token_type: string; user: User }> {
    return request('/auth/apple', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async login(data: any): Promise<{ access_token: string; token_type: string; user: User }> {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async forgotPassword(email: string): Promise<{ message: string; reset_token?: string; reset_url?: string }> {
    if (isDemoOrSocialToken()) {
      return { message: 'Demo Mode: Password reset link simulated.' };
    }
    return request('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async resetPassword(data: any): Promise<{ message: string }> {
    if (isDemoOrSocialToken()) {
      return { message: 'Demo Mode: Password has been reset.' };
    }
    return request('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getMe(): Promise<User> {
    if (isDemoOrSocialToken()) {
      return {
        id: 9999,
        email: 'guest@lokr.ai',
        name: 'Guest Explorer',
        bio: 'Exploring LOKR AI in interactive Demo Mode on GitHub Pages.',
        profile_image: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
    return request('/auth/me');
  },

  // Users & Profile
  async getProfile(): Promise<{ user: User; stats: UserStats }> {
    if (isDemoOrSocialToken()) {
      const convs = getDemoConversations();
      const totalMsgs = convs.reduce((acc, c) => acc + c.messages.length, 0);
      return {
        user: {
          id: 9999,
          email: 'guest@lokr.ai',
          name: 'Guest Explorer',
          bio: 'Exploring LOKR AI in interactive Demo Mode on GitHub Pages.',
          profile_image: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        stats: {
          conversation_count: convs.length,
          message_count: totalMsgs,
        },
      };
    }
    return request('/users/profile');
  },

  async updateProfile(data: { name?: string; bio?: string }): Promise<User> {
    if (isDemoOrSocialToken()) {
      return {
        id: 9999,
        email: 'guest@lokr.ai',
        name: data.name || 'Guest Explorer',
        bio: data.bio || 'Exploring LOKR AI in interactive Demo Mode on GitHub Pages.',
        profile_image: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
    return request('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async uploadAvatar(file: File): Promise<User> {
    if (isDemoOrSocialToken()) {
      return {
        id: 9999,
        email: 'guest@lokr.ai',
        name: 'Guest Explorer',
        bio: 'Exploring LOKR AI in interactive Demo Mode on GitHub Pages.',
        profile_image: URL.createObjectURL(file),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
    const formData = new FormData();
    formData.append('file', file);
    return request('/users/avatar', {
      method: 'POST',
      body: formData,
    });
  },

  async changePassword(data: any): Promise<{ message: string }> {
    if (isDemoOrSocialToken()) {
      return { message: 'Demo Mode: Password changed successfully.' };
    }
    return request('/users/change-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Conversations
  async getConversations(searchTerm?: string): Promise<Conversation[]> {
    if (isDemoOrSocialToken()) {
      const convs = getDemoConversations();
      if (searchTerm) {
        const q = searchTerm.toLowerCase();
        return convs
          .filter((c) => c.title.toLowerCase().includes(q))
          .map(({ id, title, created_at, updated_at }) => ({ id, title, created_at, updated_at }));
      }
      return convs.map(({ id, title, created_at, updated_at }) => ({ id, title, created_at, updated_at }));
    }
    const query = searchTerm ? `?q=${encodeURIComponent(searchTerm)}` : '';
    return request(`/chats${query}`);
  },

  async getConversation(id: number): Promise<ConversationDetail> {
    if (isDemoOrSocialToken()) {
      const convs = getDemoConversations();
      const found = convs.find((c) => c.id === id);
      if (!found) throw new ApiError('Conversation not found', 404);
      return found as ConversationDetail;
    }
    return request(`/chats/${id}`);
  },

  async createConversation(title?: string): Promise<Conversation> {
    if (isDemoOrSocialToken()) {
      const convs = getDemoConversations();
      const newConv: DemoConvData = {
        id: Date.now(),
        title: title || 'New Chat',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: [],
      };
      convs.unshift(newConv);
      saveDemoConversations(convs);
      return { id: newConv.id, title: newConv.title, created_at: newConv.created_at, updated_at: newConv.updated_at };
    }
    return request('/chats', {
      method: 'POST',
      body: JSON.stringify({ title: title || 'New Chat' }),
    });
  },

  async updateConversation(id: number, title: string): Promise<Conversation> {
    if (isDemoOrSocialToken()) {
      const convs = getDemoConversations();
      const c = convs.find((item) => item.id === id);
      if (c) {
        c.title = title;
        c.updated_at = new Date().toISOString();
        saveDemoConversations(convs);
        return { id: c.id, title: c.title, created_at: c.created_at, updated_at: c.updated_at };
      }
      throw new ApiError('Conversation not found', 404);
    }
    return request(`/chats/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title }),
    });
  },

  async deleteConversation(id: number): Promise<{ message: string }> {
    if (isDemoOrSocialToken()) {
      let convs = getDemoConversations();
      convs = convs.filter((c) => c.id !== id);
      saveDemoConversations(convs);
      return { message: 'Conversation deleted' };
    }
    return request(`/chats/${id}`, {
      method: 'DELETE',
    });
  },

  async clearAllConversations(): Promise<{ message: string }> {
    if (isDemoOrSocialToken()) {
      saveDemoConversations([]);
      return { message: 'All conversations cleared' };
    }
    return request('/chats', {
      method: 'DELETE',
    });
  },

  // Files
  async uploadFile(file: File): Promise<UploadedFileInfo> {
    if (isDemoOrSocialToken()) {
      return {
        file_name: file.name,
        file_url: URL.createObjectURL(file),
        file_type: file.type || 'text/plain',
        file_size: file.size || 1024,
        extracted_text: `Demo extracted content from attached file: ${file.name}`,
      };
    }
    const formData = new FormData();
    formData.append('file', file);
    return request('/files/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Settings
  async getSettings(): Promise<UserSettings> {
    if (isDemoOrSocialToken()) {
      try {
        const saved = localStorage.getItem(DEMO_SETTINGS_KEY);
        if (saved) return JSON.parse(saved);
      } catch {}
      return {
        theme: 'system',
        enter_to_send: true,
        show_timestamps: true,
        default_model: 'qwen/qwen3.8-27b',
        system_prompt: null,
      };
    }
    return request('/settings');
  },

  async updateSettings(data: Partial<UserSettings>): Promise<UserSettings> {
    if (isDemoOrSocialToken()) {
      const current = await this.getSettings();
      const updated: UserSettings = {
        ...current,
        ...data,
      };
      try {
        localStorage.setItem(DEMO_SETTINGS_KEY, JSON.stringify(updated));
      } catch {}
      return updated;
    }
    return request('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteAccount(password: string): Promise<{ message: string }> {
    if (isDemoOrSocialToken()) {
      localStorage.removeItem(DEMO_STORAGE_KEY);
      localStorage.removeItem(DEMO_SETTINGS_KEY);
      removeToken();
      return { message: 'Demo mode reset' };
    }
    return request('/settings/account', {
      method: 'DELETE',
      body: JSON.stringify({ password }),
    });
  },

  // Real-Time Chat SSE Stream
  streamChat(
    payload: {
      conversation_id?: number | null;
      content: string;
      file_name?: string | null;
      file_url?: string | null;
      file_type?: string | null;
      file_extracted_text?: string | null;
      enable_web_search?: boolean;
      enable_image_generation?: boolean;
      model?: string;
      client_timezone?: string;
    },
    callbacks: {
      onInit?: (data: { conversation_id: number; title: string; user_message_id: number }) => void;
      onStatus?: (message: string) => void;
      onSources?: (sources: Source[]) => void;
      onImage?: (data: { image_url: string; prompt: string }) => void;
      onToken?: (token: string) => void;
      onDone?: (data: { conversation_id: number; message_id: number; title: string; sources: Source[]; image_url?: string; file_type?: string }) => void;
      onError?: (error: string) => void;
    },
    signal?: AbortSignal
  ): Promise<void> {
    const token = getToken();

    // In Demo/Social Mode: simulate realistic streaming responses
    if (isDemoOrSocialToken(token)) {
      return new Promise(async (resolve) => {
        const convs = getDemoConversations();
        const convId: number = payload.conversation_id || Date.now();
        let targetConv = convs.find((c) => c.id === convId);

        if (!targetConv) {
          targetConv = {
            id: convId,
            title: payload.content.slice(0, 30) || 'Demo Chat',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            messages: [],
          };
          convs.unshift(targetConv);
        }

        const userMsgId = Date.now();
        targetConv.messages.push({
          id: userMsgId,
          conversation_id: convId,
          role: 'user',
          content: payload.content,
          file_name: payload.file_name,
          file_url: payload.file_url,
          file_type: payload.file_type,
          created_at: new Date().toISOString(),
        });
        saveDemoConversations(convs);

        callbacks.onInit?.({
          conversation_id: convId,
          title: targetConv.title,
          user_message_id: userMsgId,
        });

        if (payload.enable_web_search) {
          callbacks.onStatus?.('Searching the web for verified sources...');
          await new Promise((r) => setTimeout(r, 600));
          callbacks.onSources?.([
            {
              title: 'Live Information Synthesis',
              url: 'https://github.com/Jlohithkrishna01/Ai_App',
              source_name: 'DuckDuckGo Web',
              snippet: 'Real-time search results synthesized into assistant response.',
            },
          ]);
          callbacks.onStatus?.('Synthesizing search results...');
          await new Promise((r) => setTimeout(r, 400));
        }

        callbacks.onStatus?.('LOKR AI is thinking...');

        const lowerTrim = payload.content.trim().toLowerCase();
        const isPureGreeting = /^(hi|hello|hey|hey there|hi there|hello there|good morning|good afternoon|good evening|greetings|howdy)(\s+(lokr(\s+ai)?|assistant))?[!.\s]*$/i.test(payload.content.trim());
        let demoResponseText = '';

        if (isPureGreeting) {
          const isReturning = targetConv.messages.length > 2 || convs.length > 1;
          let activeName: string | null = null;
          try {
            const rawUser = localStorage.getItem('lokr_user') || localStorage.getItem('user');
            if (rawUser) {
              const parsed = JSON.parse(rawUser);
              activeName = parsed.name || null;
            }
          } catch {}

          const prefName = extractPreferredName(activeName);
          if (lowerTrim.includes('hello')) {
            demoResponseText = prefName
              ? `Hello ${prefName}! 👋\nNice to see you. How can I help you today?`
              : `Hello! 👋 Nice to see you. How can I help you today?`;
          } else if (lowerTrim.includes('hey')) {
            demoResponseText = prefName
              ? `Hey ${prefName}! 👋\nWhat can I help you with today?`
              : `Hey! 👋 What can I help you with today?`;
          } else if (lowerTrim.includes('good morning')) {
            demoResponseText = prefName
              ? `Good morning, ${prefName}! 👋\nHow can I help you today?`
              : `Good morning! 👋 How can I help you today?`;
          } else if (isReturning) {
            demoResponseText = prefName
              ? `Welcome back, ${prefName}! 👋\nWhat would you like to work on today?`
              : `Welcome back! 👋 What would you like to work on today?`;
          } else {
            demoResponseText = prefName
              ? `Hi ${prefName}! 👋\nHow can I help you today?`
              : `Hi! 👋 How can I help you today?`;
          }
        } else if (/^(what('?s| is) your name|who are you)[?!.\s]*$/i.test(payload.content.trim())) {
          demoResponseText = "I'm LOKR AI, your AI assistant. How can I help you?";
        } else if (/^(how are you|how'?re you)[?!.\s]*$/i.test(payload.content.trim())) {
          demoResponseText = "I'm doing well, thank you for asking! How can I help you today?";
        } else if (payload.file_name) {
          demoResponseText = `I have received and analyzed your document **${payload.file_name}**.\n\n### Document Summary\n- **Filename**: \`${payload.file_name}\`\n- **Status**: Processed successfully\n\nBased on your query: "${payload.content}", everything looks great! Feel free to ask specific questions about your document.`;
        } else if (/\b(what time|current time|time now|today'?s date|date today|what day is today|what date is|time in|tomorrow'?s date|next monday)\b/i.test(payload.content)) {
          const now = new Date();
          const tz = payload.client_timezone || (typeof Intl !== 'undefined' ? Intl.DateTimeFormat().resolvedOptions().timeZone : 'Asia/Kolkata');
          const timeStr = now.toLocaleTimeString('en-US', { timeZone: tz, hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: true });
          const dateStr = now.toLocaleDateString('en-US', { timeZone: tz, weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
          demoResponseText = `The current time is **${timeStr}** and today's date is **${dateStr}** (${tz}).`;
        } else {
          demoResponseText = `Thank you for your message! Here is an answer to your request:\n\n> "${payload.content}"\n\n### LOKR AI Capabilities Demo\nHere is a code example highlighting Markdown and syntax highlighting:\n\n\`\`\`typescript\n// Fast token streaming & context management\ninterface ChatState {\n  conversationId: number;\n  tokens: string[];\n  status: 'ready' | 'generating';\n}\n\nexport function calculateThroughput(tokens: number, seconds: number): number {\n  return Math.round(tokens / seconds);\n}\n\`\`\`\n\n- **Real-Time Streaming**: Tokens stream dynamically to your screen\n- **Markdown & Code**: Full formatting and syntax highlighting\n- **Web Search**: Dynamic citation cards and links\n- **Theme Support**: Seamless Light/Dark/System modes\n\n*Note*: You are in browser Demo Mode. To connect the real Groq AI backend and MySQL database, simply run **\`start-all.bat\`** on your machine or deploy the FastAPI backend!`;
        }
        const words = demoResponseText.split(/(\s+)/);
        for (const word of words) {
          if (signal?.aborted) break;
          callbacks.onToken?.(word);
          await new Promise((r) => setTimeout(r, 15));
        }

        const aiMsgId = Date.now() + 1;
        const demoSources: Source[] = payload.enable_web_search
          ? [
              {
                title: 'Live Information Synthesis',
                url: 'https://github.com/Jlohithkrishna01/Ai_App',
                source_name: 'DuckDuckGo Web',
                snippet: 'Real-time search results synthesized into assistant response.',
              },
            ]
          : [];

        targetConv.messages.push({
          id: aiMsgId,
          conversation_id: convId,
          role: 'assistant',
          content: demoResponseText,
          created_at: new Date().toISOString(),
          sources: demoSources,
        });
        saveDemoConversations(convs);

        callbacks.onDone?.({
          conversation_id: convId,
          message_id: aiMsgId,
          title: targetConv.title,
          sources: demoSources,
        });
        resolve();
      });
    }

    return new Promise(async (resolve, reject) => {
      try {
        let response: Response;
        try {
          response = await fetch(`${API_BASE}/ai/chat/stream`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({
              ...payload,
              client_timezone: payload.client_timezone || (typeof Intl !== 'undefined' ? Intl.DateTimeFormat().resolvedOptions().timeZone : 'Asia/Kolkata'),
            }),
            signal,
          });
        } catch (fetchErr: any) {
          const isGH = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
          const errorMsg = isGH
            ? 'Backend not connected on GitHub Pages. Try Demo Mode or connect a live cloud backend!'
            : 'Cannot connect to backend server. Make sure the backend is running on http://127.0.0.1:8000.';
          callbacks.onError?.(errorMsg);
          reject(new Error(errorMsg));
          return;
        }

        if (!response.ok) {
          let errorMsg = 'Failed to connect to AI stream.';
          const isGH = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
          if (response.status === 404 && isGH) {
            errorMsg = 'Backend API is not hosted on GitHub Pages. Switch to Demo Mode to test chat in the browser!';
          } else {
            try {
              const err = await response.json();
              errorMsg = err.detail || errorMsg;
            } catch {}
          }
          callbacks.onError?.(errorMsg);
          reject(new Error(errorMsg));
          return;
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('ReadableStream not supported by browser.');
        }

        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let receivedTokens = false;
        let receivedDone = false;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data: ')) {
              const jsonStr = trimmed.slice(6);
              try {
                const event = JSON.parse(jsonStr);
                if (event.type === 'init') {
                  callbacks.onInit?.(event);
                } else if (event.type === 'status') {
                  callbacks.onStatus?.(event.message);
                } else if (event.type === 'sources') {
                  callbacks.onSources?.(event.sources);
                } else if (event.type === 'image') {
                  callbacks.onImage?.(event);
                } else if (event.type === 'token') {
                  receivedTokens = true;
                  callbacks.onToken?.(event.content);
                } else if (event.type === 'done') {
                  receivedDone = true;
                  callbacks.onDone?.(event);
                } else if (event.type === 'error') {
                  callbacks.onError?.(event.message);
                }
              } catch (parseErr) {
                console.error('Error parsing SSE event:', parseErr, jsonStr);
              }
            }
          }
        }

        // Safety fallback: If stream closed without receiving an explicit 'done' event
        if (!receivedDone) {
          if (receivedTokens) {
            callbacks.onDone?.({
              conversation_id: payload.conversation_id || Date.now(),
              message_id: Date.now(),
              title: payload.content.slice(0, 30) || 'Chat',
              sources: [],
            });
          } else {
            callbacks.onError?.("The AI stream closed unexpectedly before sending response tokens. Please check server logs.");
          }
        }
        resolve();
      } catch (err: any) {
        if (err.name === 'AbortError') {
          console.log('Stream generation aborted by user.');
          resolve();
        } else {
          callbacks.onError?.(err.message || 'Stream connection lost.');
          reject(err);
        }
      }
    });
  }
};
