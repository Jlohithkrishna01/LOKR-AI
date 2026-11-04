import React, { useState, useEffect } from 'react';
import {
  User,
  Palette,
  MessageSquare,
  ShieldAlert,
  Sun,
  Moon,
  Laptop,
  AlertTriangle,
} from 'lucide-react';
import { Modal } from '../common/Modal';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useChat } from '../../context/ChatContext';
import { api } from '../../services/api';
import { UserSettings } from '../../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenChangePassword?: () => void;
  onOpenEditProfile?: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  onOpenChangePassword,
  onOpenEditProfile,
}) => {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const { clearAllConversations } = useChat();

  const [activeTab, setActiveTab] = useState<'account' | 'appearance' | 'chat' | 'privacy'>('account');
  const [settings, setSettings] = useState<UserSettings>({
    theme: 'dark',
    enter_to_send: true,
    show_timestamps: true,
    default_model: 'qwen/qwen3.8-27b',
    system_prompt: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  };

  const handleUpdateSetting = async (key: keyof UserSettings, value: any) => {
    const updated = { ...settings, [key]: value };
    setSettings(updated);
    try {
      await api.updateSettings({ [key]: value });
    } catch (err) {
      console.error('Failed to save setting:', err);
    }
  };

  const handleClearHistory = async () => {
    if (confirm('Are you sure you want to clear your entire chat history? This action cannot be undone.')) {
      await clearAllConversations();
      alert('Chat history cleared successfully.');
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      setDeleteError('Please enter your password to confirm account deletion.');
      return;
    }

    if (!confirm('WARNING: This will permanently delete your account and all associated data. Are you absolutely sure?')) {
      return;
    }

    setIsLoading(true);
    setDeleteError(null);
    try {
      await api.deleteAccount(deletePassword);
      logout();
    } catch (err: any) {
      setDeleteError(err.message || 'Failed to delete account.');
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'account', label: 'Account', icon: <User className="w-4 h-4" /> },
    { id: 'appearance', label: 'Appearance', icon: <Palette className="w-4 h-4" /> },
    { id: 'chat', label: 'Chat', icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'privacy', label: 'Privacy', icon: <ShieldAlert className="w-4 h-4" /> },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Settings" maxWidth="max-w-2xl">
      <div className="flex flex-col sm:flex-row gap-6 min-h-[380px]">
        {/* Navigation Tabs (Sidebar style) */}
        <div className="sm:w-44 flex sm:flex-col gap-1 border-b sm:border-b-0 sm:border-r border-neutral-200 dark:border-neutral-800 pb-3 sm:pb-0 sm:pr-3 shrink-0 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-colors text-left shrink-0 ${
                activeTab === tab.id
                  ? 'bg-black text-white dark:bg-white dark:text-black font-semibold'
                  : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-[#252525] hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content Panel */}
        <div className="flex-1 overflow-y-auto">
          {/* ACCOUNT TAB */}
          {activeTab === 'account' && (
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-neutral-900 dark:text-white mb-1">
                  Account Details
                </h4>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Manage your personal account credentials.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800 space-y-3">
                <div>
                  <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
                    Full Name
                  </label>
                  <p className="text-sm font-medium text-neutral-900 dark:text-white mt-0.5">
                    {user?.name}
                  </p>
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
                    Email Address
                  </label>
                  <p className="text-sm font-medium text-neutral-900 dark:text-white mt-0.5">
                    {user?.email}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 pt-2">
                {onOpenEditProfile && (
                  <button
                    onClick={() => {
                      onClose();
                      onOpenEditProfile();
                    }}
                    type="button"
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-neutral-100 dark:bg-[#252525] text-neutral-800 dark:text-neutral-200 hover:bg-neutral-200 dark:hover:bg-[#303030] transition-colors"
                  >
                    Edit Profile
                  </button>
                )}
                {onOpenChangePassword && (
                  <button
                    onClick={() => {
                      onClose();
                      onOpenChangePassword();
                    }}
                    type="button"
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-neutral-100 dark:bg-[#252525] text-neutral-800 dark:text-neutral-200 hover:bg-neutral-200 dark:hover:bg-[#303030] transition-colors"
                  >
                    Change Password
                  </button>
                )}
              </div>
            </div>
          )}

          {/* APPEARANCE TAB */}
          {activeTab === 'appearance' && (
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-neutral-900 dark:text-white mb-1">
                  Theme Preference
                </h4>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Choose your interface appearance.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setTheme('light');
                    handleUpdateSetting('theme', 'light');
                  }}
                  className={`flex flex-col items-center gap-2.5 p-4 rounded-2xl border transition-colors text-center ${
                    theme === 'light'
                      ? 'border-neutral-900 dark:border-white bg-neutral-100 dark:bg-[#252525]'
                      : 'border-neutral-200 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-[#202020]'
                  }`}
                >
                  <Sun className="w-5 h-5 text-neutral-800 dark:text-neutral-200" />
                  <span className="text-xs font-medium text-neutral-900 dark:text-white">
                    Light
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setTheme('dark');
                    handleUpdateSetting('theme', 'dark');
                  }}
                  className={`flex flex-col items-center gap-2.5 p-4 rounded-2xl border transition-colors text-center ${
                    theme === 'dark'
                      ? 'border-neutral-900 dark:border-white bg-neutral-100 dark:bg-[#252525]'
                      : 'border-neutral-200 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-[#202020]'
                  }`}
                >
                  <Moon className="w-5 h-5 text-neutral-800 dark:text-neutral-200" />
                  <span className="text-xs font-medium text-neutral-900 dark:text-white">
                    Dark
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setTheme('system');
                    handleUpdateSetting('theme', 'system');
                  }}
                  className={`flex flex-col items-center gap-2.5 p-4 rounded-2xl border transition-colors text-center ${
                    theme === 'system'
                      ? 'border-neutral-900 dark:border-white bg-neutral-100 dark:bg-[#252525]'
                      : 'border-neutral-200 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-[#202020]'
                  }`}
                >
                  <Laptop className="w-5 h-5 text-neutral-800 dark:text-neutral-200" />
                  <span className="text-xs font-medium text-neutral-900 dark:text-white">
                    System
                  </span>
                </button>
              </div>
            </div>
          )}

          {/* CHAT TAB */}
          {activeTab === 'chat' && (
            <div className="space-y-5">
              <div>
                <h4 className="text-sm font-semibold text-neutral-900 dark:text-white mb-1">
                  Chat Preferences
                </h4>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Customize the chat interface and AI behavior.
                </p>
              </div>

              {/* Enter to Send Toggle */}
              <div className="flex items-center justify-between p-3.5 rounded-2xl bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800">
                <div>
                  <p className="text-xs font-semibold text-neutral-900 dark:text-white">
                    Enter key sends message
                  </p>
                  <p className="text-[11px] text-neutral-500 dark:text-neutral-400 mt-0.5">
                    When disabled, use Shift + Enter or the Send button
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.enter_to_send}
                  onChange={(e) => handleUpdateSetting('enter_to_send', e.target.checked)}
                  className="w-4 h-4 rounded text-neutral-900 dark:text-white border-neutral-300 dark:border-neutral-700"
                />
              </div>

              {/* Timestamps Toggle */}
              <div className="flex items-center justify-between p-3.5 rounded-2xl bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800">
                <div>
                  <p className="text-xs font-semibold text-neutral-900 dark:text-white">
                    Show message timestamps
                  </p>
                  <p className="text-[11px] text-neutral-500 dark:text-neutral-400 mt-0.5">
                    Display time of delivery next to messages
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.show_timestamps}
                  onChange={(e) => handleUpdateSetting('show_timestamps', e.target.checked)}
                  className="w-4 h-4 rounded text-neutral-900 dark:text-white border-neutral-300 dark:border-neutral-700"
                />
              </div>

              {/* AI Model Selector */}
              <div>
                <label className="block text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-1">
                  Default AI Model
                </label>
                <select
                  value={settings.default_model}
                  onChange={(e) => handleUpdateSetting('default_model', e.target.value)}
                  className="w-full px-3 py-2 rounded-xl text-xs bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-white focus:outline-none"
                >
                  <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Anthropic - State of the Art)</option>
                  <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku (Anthropic - Ultra Fast)</option>
                  <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Fast, Highly Accurate)</option>
                  <option value="openai/gpt-oss-120b">GPT OSS 120B (Deep Reasoning)</option>
                  <option value="openai/gpt-oss-20b">GPT OSS 20B (Compact, Ultra Fast)</option>
                </select>
              </div>

              {/* Custom System Prompt */}
              <div>
                <label className="block text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-1">
                  Custom AI Instructions (Optional)
                </label>
                <textarea
                  value={settings.system_prompt || ''}
                  onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                  onBlur={() => handleUpdateSetting('system_prompt', settings.system_prompt)}
                  placeholder="e.g. Always respond in concise bullet points..."
                  rows={2}
                  className="w-full px-3.5 py-2 rounded-xl text-xs bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-white focus:outline-none resize-none"
                />
              </div>
            </div>
          )}

          {/* PRIVACY TAB */}
          {activeTab === 'privacy' && (
            <div className="space-y-5">
              <div>
                <h4 className="text-sm font-semibold text-neutral-900 dark:text-white mb-1">
                  Privacy & Data Management
                </h4>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Control your conversation data and account lifecycle.
                </p>
              </div>

              {/* Clear Chat History */}
              <div className="p-4 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#212121]">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-xs font-semibold text-neutral-900 dark:text-white">
                      Clear all chat history
                    </h5>
                    <p className="text-[11px] text-neutral-500 dark:text-neutral-400 mt-0.5">
                      Permanently delete all previous conversations and messages.
                    </p>
                  </div>
                  <button
                    onClick={handleClearHistory}
                    type="button"
                    className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-rose-500 border border-rose-500/30 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors shrink-0"
                  >
                    Clear History
                  </button>
                </div>
              </div>

              {/* Delete Account */}
              <div className="p-4 rounded-2xl border border-rose-500/30 bg-rose-50/20 dark:bg-rose-950/20 space-y-3">
                <div className="flex items-start gap-2.5 text-rose-500">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <div>
                    <h5 className="text-xs font-semibold">Delete Account</h5>
                    <p className="text-[11px] text-neutral-600 dark:text-neutral-300 mt-0.5">
                      Permanently delete your LOKR AI account and all stored history. This action cannot be reversed.
                    </p>
                  </div>
                </div>

                {deleteError && (
                  <p className="text-xs text-rose-500 font-medium">{deleteError}</p>
                )}

                <div className="pt-1">
                  <input
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder="Enter your current password to confirm"
                    className="w-full px-3 py-2 rounded-xl text-xs bg-white dark:bg-[#181818] border border-rose-500/40 text-neutral-900 dark:text-white focus:outline-none"
                  />
                  <button
                    onClick={handleDeleteAccount}
                    disabled={isLoading || !deletePassword}
                    type="button"
                    className="mt-2.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 transition-colors disabled:opacity-50"
                  >
                    {isLoading ? 'Deleting...' : 'Delete My Account'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};
