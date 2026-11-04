import React, { useState, useRef, useEffect } from 'react';
import {
  ArrowUp,
  Square,
  Paperclip,
  Mic,
  MicOff,
  Globe,
  Palette,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { api } from '../../services/api';
import { UploadedFileInfo } from '../../types';
import { FilePreviewChip } from './FilePreviewChip';

interface ChatInputProps {
  onSend: (params: {
    content: string;
    fileInfo?: UploadedFileInfo | null;
    enableWebSearch: boolean;
    enableImageGeneration?: boolean;
  }) => void;
  onStop: () => void;
  isStreaming: boolean;
  enterToSend?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onStop,
  isStreaming,
  enterToSend = true,
}) => {
  const [content, setContent] = useState('');
  const [fileInfo, setFileInfo] = useState<UploadedFileInfo | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [enableWebSearch, setEnableWebSearch] = useState(false);
  const [enableImageGeneration, setEnableImageGeneration] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [content]);

  // Focus textarea when not streaming
  useEffect(() => {
    if (!isStreaming && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isStreaming]);

  // Speech Recognition setup
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setContent((prev) => (prev ? `${prev} ${transcript}` : transcript));
        setIsListening(false);
      };

      recognition.onerror = (err: any) => {
        console.error('Speech recognition error:', err);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter') {
      if (enterToSend && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    }
  };

  const handleSend = () => {
    if ((!content.trim() && !fileInfo) || isStreaming) return;
    onSend({
      content: content.trim(),
      fileInfo,
      enableWebSearch,
      enableImageGeneration,
    });
    setContent('');
    setFileInfo(null);
    setUploadError(null);
    setEnableImageGeneration(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const uploaded = await api.uploadFile(file);
      setFileInfo(uploaded);
    } catch (err: any) {
      setUploadError(err.message || 'File upload failed.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const canSubmit = (content.trim().length > 0 || !!fileInfo) && !isUploading;

  return (
    <div className="w-full max-w-3xl lg:max-w-4xl mx-auto px-4 pb-4 pt-1">
      {/* Upload Error Banner */}
      {uploadError && (
        <div className="mb-2 flex items-center gap-2 p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Main Input Container Card */}
      <div className="relative rounded-2xl sm:rounded-3xl border border-neutral-300 dark:border-neutral-700/80 bg-white dark:bg-[#212121] shadow-sm focus-within:border-neutral-400 dark:focus-within:border-neutral-500 transition-colors">
        {/* Attached file preview chip */}
        {(fileInfo || isUploading) && (
          <div className="p-3 pb-0">
            <FilePreviewChip
              fileInfo={fileInfo}
              isLoading={isUploading}
              onRemove={() => setFileInfo(null)}
            />
          </div>
        )}

        {/* Text Area */}
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            enableImageGeneration
              ? "Describe an image to generate..."
              : "Message LOKR AI..."
          }
          rows={1}
          className="w-full px-4 pt-3.5 pb-2 bg-transparent text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 dark:placeholder-neutral-500 resize-none focus:outline-none text-sm sm:text-base leading-relaxed"
          style={{ maxHeight: '200px' }}
        />

        {/* Bottom Toolbar & Action Buttons */}
        <div className="flex items-center justify-between px-3 py-2 border-t border-neutral-100 dark:border-neutral-800/80">
          {/* Left Action Buttons */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {/* File Upload Button */}
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              className="hidden"
              accept=".pdf,.docx,.doc,.txt,.csv,.md,.json,.png,.jpg,.jpeg,.webp"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              type="button"
              disabled={isUploading || isStreaming}
              className="p-2 rounded-xl text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#2b2b2b] transition-colors disabled:opacity-50"
              title="Attach document or image (PDF, DOCX, TXT, CSV, Image)"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            {/* Create Image Toggle Button */}
            <button
              onClick={() => {
                setEnableImageGeneration(!enableImageGeneration);
                if (!enableImageGeneration) setEnableWebSearch(false);
              }}
              type="button"
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium transition-colors ${
                enableImageGeneration
                  ? 'bg-neutral-900 text-white dark:bg-white dark:text-black font-semibold'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#2b2b2b]'
              }`}
              title="Generate image with AI"
            >
              <Palette className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Create Image</span>
            </button>

            {/* Web Search Toggle Button */}
            <button
              onClick={() => {
                setEnableWebSearch(!enableWebSearch);
                if (!enableWebSearch) setEnableImageGeneration(false);
              }}
              type="button"
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium transition-colors ${
                enableWebSearch
                  ? 'bg-neutral-900 text-white dark:bg-white dark:text-black font-semibold'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#2b2b2b]'
              }`}
              title="Search the web for real-time information"
            >
              <Globe className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Web Search</span>
            </button>

            {/* Voice Input Button */}
            <button
              onClick={toggleVoiceInput}
              type="button"
              className={`p-2 rounded-xl transition-colors ${
                isListening
                  ? 'text-rose-500 bg-rose-50 dark:bg-rose-950/40 animate-pulse'
                  : 'text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#2b2b2b]'
              }`}
              title={isListening ? 'Listening... click to stop' : 'Voice input'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          </div>

          {/* Right Action: Send / Stop Generating Button */}
          <div className="flex items-center gap-2">
            {isStreaming ? (
              <button
                onClick={onStop}
                type="button"
                className="w-8 h-8 rounded-full bg-black text-white hover:bg-neutral-800 dark:bg-white dark:text-black dark:hover:bg-neutral-200 flex items-center justify-center transition-all shadow-sm"
                title="Stop generating"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!canSubmit}
                type="button"
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all shadow-sm ${
                  canSubmit
                    ? 'bg-black text-white hover:bg-neutral-800 dark:bg-white dark:text-black dark:hover:bg-neutral-200 cursor-pointer'
                    : 'bg-neutral-200 text-neutral-400 dark:bg-neutral-800 dark:text-neutral-600 cursor-not-allowed'
                }`}
                title="Send message"
              >
                {isUploading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="mt-2 text-center text-[11px] text-neutral-400 dark:text-neutral-500">
        LOKR AI can make mistakes. Verify important information.
      </div>
    </div>
  );
};
