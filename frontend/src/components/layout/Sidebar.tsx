import React, { useState } from 'react';
import {
  Plus,
  Search,
  MessageSquare,
  Edit2,
  Trash2,
  Check,
  X,
  Settings as SettingsIcon,
  LogOut,
  ChevronLeft,
} from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useAuth } from '../../context/AuthContext';
import { Logo } from '../common/Logo';
import { Avatar } from '../common/Avatar';
import { ThemeToggle } from '../common/ThemeToggle';
import { Conversation } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onOpenProfile: () => void;
  onOpenSettings: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  onOpenProfile,
  onOpenSettings,
}) => {
  const { user, logout } = useAuth();
  const {
    groupedConversations,
    currentConversationId,
    selectConversation,
    startNewChat,
    renameConversation,
    deleteConversation,
    searchTerm,
    setSearchTerm,
    conversations,
  } = useChat();

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleStartRename = (conv: Conversation, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditingTitle(conv.title);
  };

  const handleSaveRename = async (id: number, e: React.MouseEvent | React.FormEvent) => {
    e.stopPropagation();
    if (editingTitle.trim()) {
      await renameConversation(id, editingTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      await deleteConversation(id);
    }
  };

  const renderConversationGroup = (title: string, items: Conversation[]) => {
    if (items.length === 0) return null;

    return (
      <div key={title} className="mb-4">
        <h4 className="px-3 mb-1 text-[11px] font-semibold tracking-wider uppercase text-neutral-400 dark:text-neutral-500">
          {title}
        </h4>
        <div className="space-y-0.5">
          {items.map((conv) => {
            const isActive = currentConversationId === conv.id;
            const isEditing = editingId === conv.id;

            return (
              <div
                key={conv.id}
                onClick={() => {
                  if (!isEditing) {
                    selectConversation(conv.id);
                    if (window.innerWidth < 1024) onToggle();
                  }
                }}
                className={`group relative flex items-center justify-between px-3 py-2 rounded-xl text-sm cursor-pointer transition-colors duration-150 ${
                  isActive
                    ? 'bg-neutral-200/75 dark:bg-[#262626] text-neutral-900 dark:text-white font-medium'
                    : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-[#212121] hover:text-neutral-900 dark:hover:text-white'
                }`}
              >
                {isEditing ? (
                  <form
                    onSubmit={(e) => handleSaveRename(conv.id, e)}
                    className="flex items-center gap-1 w-full"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      autoFocus
                      className="flex-1 px-2 py-1 text-xs rounded-lg bg-white dark:bg-[#141414] border border-neutral-400 dark:border-neutral-600 text-neutral-900 dark:text-white focus:outline-none"
                    />
                    <button
                      type="submit"
                      className="p-1 text-emerald-600 hover:text-emerald-500"
                      title="Save"
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={handleCancelRename}
                      className="p-1 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
                      title="Cancel"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </form>
                ) : (
                  <>
                    <div className="flex items-center gap-2.5 truncate flex-1 min-w-0 mr-2">
                      <MessageSquare className={`w-4 h-4 shrink-0 ${isActive ? 'text-neutral-900 dark:text-white' : 'text-neutral-400 dark:text-neutral-500'}`} />
                      <span className="truncate">{conv.title}</span>
                    </div>

                    {/* Hover Actions (Rename / Delete) */}
                    <div className="hidden group-hover:flex items-center gap-0.5 shrink-0">
                      <button
                        onClick={(e) => handleStartRename(conv, e)}
                        type="button"
                        className="p-1 rounded-md text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/80 dark:hover:bg-[#333333] transition-colors"
                        title="Rename conversation"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(conv.id, e)}
                        type="button"
                        className="p-1 rounded-md text-neutral-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                        title="Delete conversation"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const hasAnyConversations = conversations.length > 0;

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 lg:hidden backdrop-blur-sm transition-opacity"
          onClick={onToggle}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-40 flex flex-col w-64 sm:w-72 bg-[#f9f9f9] dark:bg-[#171717] border-r border-neutral-200/80 dark:border-neutral-800/80 transition-transform duration-300 ease-in-out shrink-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:hidden'
        }`}
      >
        {/* Top Header: Logo + Collapse Button */}
        <div className="flex items-center justify-between px-4 py-3.5 border-b border-neutral-200/70 dark:border-neutral-800/70">
          <Logo size="md" />
          <button
            onClick={onToggle}
            type="button"
            className="p-1.5 rounded-lg text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/60 dark:hover:bg-neutral-800 transition-colors"
            title="Collapse sidebar"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={() => {
              startNewChat();
              if (window.innerWidth < 1024) onToggle();
            }}
            type="button"
            className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl border border-neutral-200 dark:border-neutral-700/60 bg-white dark:bg-[#212121] hover:bg-neutral-100 dark:hover:bg-[#2a2a2a] text-neutral-900 dark:text-neutral-100 font-medium text-sm transition-colors shadow-sm"
          >
            <div className="flex items-center gap-2.5">
              <Plus className="w-4 h-4 text-neutral-700 dark:text-neutral-300" />
              <span>New chat</span>
            </div>
          </button>
        </div>

        {/* Search Input Field */}
        <div className="px-3 mb-2">
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 absolute left-3 text-neutral-400 dark:text-neutral-500 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search chats..."
              className="w-full pl-8 pr-7 py-1.5 rounded-xl text-xs bg-white dark:bg-[#212121] border border-neutral-200 dark:border-neutral-700/60 focus:border-neutral-400 dark:focus:border-neutral-500 text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:outline-none transition-colors"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-2.5 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Conversations History List */}
        <div className="flex-1 overflow-y-auto px-2 py-1">
          {!hasAnyConversations ? (
            <div className="h-full flex flex-col items-center justify-center p-6 text-center text-neutral-400">
              <MessageSquare className="w-7 h-7 mb-2 opacity-30 text-neutral-500" />
              <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400">
                No conversations yet
              </p>
              <p className="text-[11px] text-neutral-400 dark:text-neutral-500 mt-1">
                Start a new conversation with LOKR AI.
              </p>
            </div>
          ) : (
            <>
              {renderConversationGroup('Today', groupedConversations.today)}
              {renderConversationGroup('Yesterday', groupedConversations.yesterday)}
              {renderConversationGroup('Previous 7 Days', groupedConversations.previous7Days)}
              {renderConversationGroup('Older', groupedConversations.older)}
            </>
          )}
        </div>

        {/* Bottom Profile & Settings Section */}
        <div className="p-3 border-t border-neutral-200/80 dark:border-neutral-800/80 bg-neutral-100/50 dark:bg-[#141414]">
          <div
            onClick={onOpenProfile}
            className="flex items-center gap-3 p-2 rounded-xl hover:bg-neutral-200/60 dark:hover:bg-[#212121] cursor-pointer transition-colors"
          >
            <Avatar src={user?.profile_image} name={user?.name} size="sm" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-neutral-900 dark:text-white truncate">
                {user?.name}
              </p>
              <p className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate">
                {user?.email}
              </p>
            </div>
          </div>

          <div className="mt-1 flex items-center justify-between px-1">
            <button
              onClick={onOpenSettings}
              type="button"
              className="p-2 rounded-xl text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/60 dark:hover:bg-[#212121] transition-colors"
              title="Settings"
            >
              <SettingsIcon className="w-4 h-4" />
            </button>

            <ThemeToggle />

            <button
              onClick={logout}
              type="button"
              className="p-2 rounded-xl text-neutral-500 dark:text-neutral-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
