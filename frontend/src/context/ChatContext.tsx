import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Conversation, ConversationDetail, Message, Source, UploadedFileInfo } from '../types';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

export interface GroupedConversations {
  today: Conversation[];
  yesterday: Conversation[];
  previous7Days: Conversation[];
  older: Conversation[];
}

interface ChatContextType {
  conversations: Conversation[];
  groupedConversations: GroupedConversations;
  currentConversationId: number | null;
  currentConversation: ConversationDetail | null;
  isLoadingConversations: boolean;
  isLoadingChat: boolean;
  isStreaming: boolean;
  streamingStatus: string | null;
  streamingSources: Source[];
  streamingContent: string;
  streamingImage: { image_url: string; prompt: string } | null;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  loadConversations: (search?: string) => Promise<void>;
  selectConversation: (id: number) => Promise<void>;
  startNewChat: () => void;
  sendMessage: (params: {
    content: string;
    fileInfo?: UploadedFileInfo | null;
    enableWebSearch?: boolean;
    enableImageGeneration?: boolean;
    model?: string;
  }) => Promise<void>;
  stopGenerating: () => void;
  regenerateMessage: (lastUserMsg: Message) => Promise<void>;
  renameConversation: (id: number, newTitle: string) => Promise<void>;
  deleteConversation: (id: number) => Promise<void>;
  clearAllConversations: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetail | null>(null);
  const [isLoadingConversations, setIsLoadingConversations] = useState<boolean>(false);
  const [isLoadingChat, setIsLoadingChat] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Streaming state
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [streamingStatus, setStreamingStatus] = useState<string | null>(null);
  const [streamingSources, setStreamingSources] = useState<Source[]>([]);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [streamingImage, setStreamingImage] = useState<{ image_url: string; prompt: string } | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const loadConversations = async (search?: string) => {
    if (!isAuthenticated) return;
    setIsLoadingConversations(true);
    try {
      const list = await api.getConversations(search);
      setConversations(list);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadConversations();
    } else {
      setConversations([]);
      setCurrentConversationId(null);
      setCurrentConversation(null);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    const handler = setTimeout(() => {
      if (isAuthenticated) {
        loadConversations(searchTerm);
      }
    }, 250);
    return () => clearTimeout(handler);
  }, [searchTerm, isAuthenticated]);

  const selectConversation = async (id: number) => {
    if (currentConversationId === id) return;
    setIsLoadingChat(true);
    setCurrentConversationId(id);
    try {
      const detail = await api.getConversation(id);
      setCurrentConversation(detail);
    } catch (err) {
      console.error('Failed to load conversation details:', err);
    } finally {
      setIsLoadingChat(false);
    }
  };

  const startNewChat = () => {
    if (isStreaming) {
      stopGenerating();
    }
    setCurrentConversationId(null);
    setCurrentConversation(null);
    setStreamingContent('');
    setStreamingSources([]);
    setStreamingStatus(null);
    setStreamingImage(null);
  };

  const stopGenerating = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setStreamingStatus(null);
    setStreamingImage(null);
  };

  const sendMessage = async ({
    content,
    fileInfo,
    enableWebSearch,
    enableImageGeneration,
    model,
  }: {
    content: string;
    fileInfo?: UploadedFileInfo | null;
    enableWebSearch?: boolean;
    enableImageGeneration?: boolean;
    model?: string;
  }) => {
    if ((!content.trim() && !fileInfo) || isStreaming) return;

    // Optimistic user message
    const tempUserMsgId = Date.now();
    const optimisticUserMsg: Message = {
      id: tempUserMsgId,
      conversation_id: currentConversationId || 0,
      role: 'user',
      content: content.trim(),
      file_name: fileInfo?.file_name || null,
      file_url: fileInfo?.file_url || null,
      file_type: fileInfo?.file_type || null,
      created_at: new Date().toISOString(),
      sources: [],
    };

    if (currentConversation) {
      setCurrentConversation({
        ...currentConversation,
        messages: [...currentConversation.messages, optimisticUserMsg],
      });
    } else {
      // New conversation screen
      setCurrentConversation({
        id: 0,
        title: 'New Chat',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: [optimisticUserMsg],
      });
    }

    setIsStreaming(true);

    setStreamingStatus('LOKR AI is thinking...');
    setStreamingSources([]);
    setStreamingContent('');
    setStreamingImage(null);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let accumulatedContent = '';
    let accumulatedSources: Source[] = [];
    let resolvedConvId = currentConversationId;
    let generatedImgUrl: string | null = null;

    try {
      await api.streamChat(
        {
          conversation_id: currentConversationId,
          content: content.trim(),
          file_name: fileInfo?.file_name,
          file_url: fileInfo?.file_url,
          file_type: fileInfo?.file_type,
          file_extracted_text: fileInfo?.extracted_text,
          enable_web_search: enableWebSearch,
          enable_image_generation: enableImageGeneration,
          model,
        },
        {
          onInit: (initData) => {
            resolvedConvId = initData.conversation_id;
            setCurrentConversationId(initData.conversation_id);
            // Replace optimistic user msg id
            setCurrentConversation((prev) => {
              if (!prev) return null;
              return {
                ...prev,
                id: initData.conversation_id,
                title: initData.title || prev.title,
                messages: prev.messages.map((m) =>
                  m.id === tempUserMsgId ? { ...m, id: initData.user_message_id, conversation_id: initData.conversation_id } : m
                ),
              };
            });
          },
          onStatus: (msg) => {
            setStreamingStatus(msg);
          },
          onSources: (sources) => {
            accumulatedSources = sources;
            setStreamingSources(sources);
          },
          onImage: (imgData) => {
            generatedImgUrl = imgData.image_url;
            setStreamingImage(imgData);
          },
          onToken: (token) => {
            setStreamingStatus(null);
            accumulatedContent += token;
            setStreamingContent((prev) => prev + token);
          },
          onDone: (doneData) => {
            setIsStreaming(false);
            setStreamingStatus(null);
            const finalImgUrl = doneData.image_url || generatedImgUrl;
            const finalContent = accumulatedContent.trim() || (finalImgUrl ? '' : "Sorry, I couldn't generate a response right now. Please try again.");
            const assistantMsg: Message = {
              id: doneData.message_id || Date.now(),
              conversation_id: doneData.conversation_id,
              role: 'assistant',
              content: finalContent,
              created_at: new Date().toISOString(),
              sources: doneData.sources || accumulatedSources,
              file_url: finalImgUrl,
              file_name: finalImgUrl ? 'Generated Image' : null,
              file_type: finalImgUrl ? 'image' : null,
            };

            setCurrentConversation((prev) => {
              if (!prev) return null;
              return {
                ...prev,
                id: doneData.conversation_id,
                title: doneData.title || prev.title,
                messages: [...prev.messages, assistantMsg],
              };
            });

            setStreamingContent('');
            setStreamingSources([]);
            setStreamingImage(null);

            // Refresh conversation list in sidebar
            loadConversations(searchTerm);
          },
          onError: (errMsg) => {
            setIsStreaming(false);
            setStreamingStatus(null);
            const errorMsg: Message = {
              id: Date.now(),
              conversation_id: resolvedConvId || 0,
              role: 'assistant',
              content: `⚠️ **Error**: ${errMsg}`,
              created_at: new Date().toISOString(),
              sources: [],
            };
            setCurrentConversation((prev) => {
              if (!prev) return null;
              return {
                ...prev,
                messages: [...prev.messages, errorMsg],
              };
            });
            setStreamingContent('');
          },
        },
        controller.signal
      );
    } catch (err: any) {
      console.error('Streaming error caught:', err);
      if (!accumulatedContent && err.name !== 'AbortError') {
        const friendlyMsg: Message = {
          id: Date.now(),
          conversation_id: resolvedConvId || 0,
          role: 'assistant',
          content: `⚠️ **Unable to connect to LOKR AI**: ${err?.message || 'The server could not be reached. Please make sure the backend is running and try again.'}`,
          created_at: new Date().toISOString(),
          sources: [],
        };
        setCurrentConversation((prev) => {
          if (!prev) return null;
          if (prev.messages.some(m => m.id === friendlyMsg.id)) return prev;
          return {
            ...prev,
            messages: [...prev.messages, friendlyMsg],
          };
        });
      }
    } finally {
      setIsStreaming(false);
      setStreamingStatus(null);
      abortControllerRef.current = null;
    }
  };

  const regenerateMessage = async (lastUserMsg: Message) => {
    if (isStreaming) return;
    // Remove trailing assistant message if present
    if (currentConversation && currentConversation.messages.length > 0) {
      const msgs = [...currentConversation.messages];
      if (msgs[msgs.length - 1].role === 'assistant') {
        msgs.pop();
        setCurrentConversation({
          ...currentConversation,
          messages: msgs,
        });
      }
    }

    await sendMessage({
      content: lastUserMsg.content,
      fileInfo: lastUserMsg.file_name
        ? {
            file_name: lastUserMsg.file_name,
            file_url: lastUserMsg.file_url || '',
            file_type: lastUserMsg.file_type || '',
            file_size: 0,
            extracted_text: '',
          }
        : null,
    });
  };

  const renameConversation = async (id: number, newTitle: string) => {
    try {
      const updated = await api.updateConversation(id, newTitle);
      setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, title: updated.title } : c)));
      if (currentConversationId === id && currentConversation) {
        setCurrentConversation({ ...currentConversation, title: updated.title });
      }
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    }
  };

  const deleteConversation = async (id: number) => {
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (currentConversationId === id) {
        startNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const clearAllConversations = async () => {
    try {
      await api.clearAllConversations();
      setConversations([]);
      startNewChat();
    } catch (err) {
      console.error('Failed to clear conversations:', err);
    }
  };

  // Group conversations into Today, Yesterday, Previous 7 Days, Older
  const groupedConversations: GroupedConversations = {
    today: [],
    yesterday: [],
    previous7Days: [],
    older: [],
  };

  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const startOfYesterday = startOfToday - 24 * 60 * 60 * 1000;
  const startOf7DaysAgo = startOfToday - 7 * 24 * 60 * 60 * 1000;

  conversations.forEach((conv) => {
    const time = new Date(conv.updated_at || conv.created_at).getTime();
    if (time >= startOfToday) {
      groupedConversations.today.push(conv);
    } else if (time >= startOfYesterday) {
      groupedConversations.yesterday.push(conv);
    } else if (time >= startOf7DaysAgo) {
      groupedConversations.previous7Days.push(conv);
    } else {
      groupedConversations.older.push(conv);
    }
  });

  return (
    <ChatContext.Provider
      value={{
        conversations,
        groupedConversations,
        currentConversationId,
        currentConversation,
        isLoadingConversations,
        isLoadingChat,
        isStreaming,
        streamingStatus,
        streamingSources,
        streamingContent,
        streamingImage,
        searchTerm,
        setSearchTerm,
        loadConversations,
        selectConversation,
        startNewChat,
        sendMessage,
        stopGenerating,
        regenerateMessage,
        renameConversation,
        deleteConversation,
        clearAllConversations,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
