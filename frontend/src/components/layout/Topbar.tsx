import React, { useState, useRef, useEffect } from 'react';
import {
  Menu,
  Plus,
  User as UserIcon,
  Settings as SettingsIcon,
  KeyRound,
  LogOut,
  Moon,
  Sun,
  Laptop,
} from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { Avatar } from '../common/Avatar';
import { ThemeToggle } from '../common/ThemeToggle';

interface TopbarProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  onOpenProfile: () => void;
  onOpenEditProfile: () => void;
  onOpenSettings: () => void;
  onOpenChangePassword: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  isSidebarOpen,
  onToggleSidebar,
  onOpenProfile,
  onOpenEditProfile,
  onOpenSettings,
  onOpenChangePassword,
}) => {
  const { currentConversation, startNewChat } = useChat();
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const conversationTitle = currentConversation?.title || 'New Chat';

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between h-14 px-3 sm:px-4 bg-white/90 dark:bg-[#0d0d0d]/90 backdrop-blur-md border-b border-neutral-200/80 dark:border-neutral-800/80 transition-colors">
      {/* Left: Sidebar Toggle + Title */}
      <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
        <button
          onClick={onToggleSidebar}
          type="button"
          className="p-2 rounded-xl text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors"
          title={isSidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
        >
          <Menu className="w-5 h-5" />
        </button>

        <h2 className="text-sm sm:text-base font-semibold text-neutral-900 dark:text-white truncate">
          {conversationTitle}
        </h2>
      </div>

      {/* Right: Actions & Theme Toggle & User Avatar Menu */}
      <div className="flex items-center gap-1.5 sm:gap-2">
        <button
          onClick={startNewChat}
          type="button"
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-[#212121] border border-neutral-200 dark:border-neutral-700/60 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Chat</span>
        </button>

        {/* Prominent Light/Dark Mode Toggle in Top Navigation */}
        <ThemeToggle />

        {/* Profile Avatar & Dropdown */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            type="button"
            className="flex items-center p-0.5 rounded-full ring-2 ring-transparent hover:ring-neutral-400/40 transition-all focus:outline-none"
            aria-expanded={isMenuOpen}
          >
            <Avatar src={user?.profile_image} name={user?.name} size="sm" />
          </button>

          {/* Polished Profile Dropdown Menu */}
          {isMenuOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-white dark:bg-[#171717] border border-neutral-200 dark:border-neutral-800 shadow-xl z-50 py-2 animate-in fade-in zoom-in-95 duration-150">
              {/* User Identity Header */}
              <div className="px-4 py-3 border-b border-neutral-100 dark:border-neutral-800">
                <p className="text-sm font-semibold text-neutral-900 dark:text-white truncate">
                  {user?.name}
                </p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate mt-0.5">
                  {user?.email}
                </p>
              </div>

              {/* Menu Actions */}
              <div className="py-1">
                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onOpenProfile();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors text-left"
                >
                  <UserIcon className="w-4 h-4 text-neutral-500" />
                  <span>My Profile</span>
                </button>

                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onOpenEditProfile();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors text-left"
                >
                  <UserIcon className="w-4 h-4 text-neutral-500" />
                  <span>Edit Profile</span>
                </button>

                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onOpenChangePassword();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors text-left"
                >
                  <KeyRound className="w-4 h-4 text-neutral-500" />
                  <span>Change Password</span>
                </button>

                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    onOpenSettings();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-medium text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors text-left"
                >
                  <SettingsIcon className="w-4 h-4 text-neutral-500" />
                  <span>Settings</span>
                </button>
              </div>

              {/* Theme Selector Submenu */}
              <div className="px-4 py-2.5 border-t border-neutral-100 dark:border-neutral-800">
                <p className="text-[11px] font-semibold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider mb-2">
                  Theme
                </p>
                <div className="grid grid-cols-3 gap-1">
                  <button
                    onClick={() => setTheme('light')}
                    className={`flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg text-xs font-medium transition-colors ${
                      theme === 'light'
                        ? 'bg-neutral-900 text-white dark:bg-white dark:text-black font-semibold'
                        : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-[#212121]'
                    }`}
                  >
                    <Sun className="w-3.5 h-3.5" />
                    <span>Light</span>
                  </button>
                  <button
                    onClick={() => setTheme('dark')}
                    className={`flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg text-xs font-medium transition-colors ${
                      theme === 'dark'
                        ? 'bg-neutral-900 text-white dark:bg-white dark:text-black font-semibold'
                        : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-[#212121]'
                    }`}
                  >
                    <Moon className="w-3.5 h-3.5" />
                    <span>Dark</span>
                  </button>
                  <button
                    onClick={() => setTheme('system')}
                    className={`flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg text-xs font-medium transition-colors ${
                      theme === 'system'
                        ? 'bg-neutral-900 text-white dark:bg-white dark:text-black font-semibold'
                        : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-[#212121]'
                    }`}
                  >
                    <Laptop className="w-3.5 h-3.5" />
                    <span>Auto</span>
                  </button>
                </div>
              </div>

              {/* Logout Option */}
              <div className="pt-1 border-t border-neutral-100 dark:border-neutral-800">
                <button
                  onClick={logout}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-semibold text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors text-left"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Log out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
