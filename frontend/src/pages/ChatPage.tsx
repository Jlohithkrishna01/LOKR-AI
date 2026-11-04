import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Topbar } from '../components/layout/Topbar';
import { ChatArea } from '../components/chat/ChatArea';
import { ProfileModal } from '../components/profile/ProfileModal';
import { ChangePasswordModal } from '../components/profile/ChangePasswordModal';
import { SettingsModal } from '../components/settings/SettingsModal';
import { api } from '../services/api';
import { UserSettings } from '../types';

export const ChatPage: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
    return window.innerWidth >= 1024;
  });

  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false);

  const [userSettings, setUserSettings] = useState<UserSettings>({
    theme: 'dark',
    enter_to_send: true,
    show_timestamps: true,
    default_model: 'qwen/qwen3.8-27b',
    system_prompt: '',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await api.getSettings();
      setUserSettings(data);
    } catch (err) {
      console.error('Failed to load user settings:', err);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white dark:bg-[#0d0d0d] text-neutral-900 dark:text-neutral-100 font-sans antialiased">
      {/* Collapsible Left Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        onOpenProfile={() => setIsProfileOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative">
        <Topbar
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenProfile={() => setIsProfileOpen(true)}
          onOpenEditProfile={() => setIsEditProfileOpen(true)}
          onOpenSettings={() => setIsSettingsOpen(true)}
          onOpenChangePassword={() => setIsChangePasswordOpen(true)}
        />

        <ChatArea
          enterToSend={userSettings.enter_to_send}
          showTimestamps={userSettings.show_timestamps}
        />
      </main>

      {/* Modals */}
      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        defaultEditMode={false}
      />

      <ProfileModal
        isOpen={isEditProfileOpen}
        onClose={() => setIsEditProfileOpen(false)}
        defaultEditMode={true}
      />

      <ChangePasswordModal
        isOpen={isChangePasswordOpen}
        onClose={() => setIsChangePasswordOpen(false)}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => {
          setIsSettingsOpen(false);
          loadSettings();
        }}
        onOpenChangePassword={() => setIsChangePasswordOpen(true)}
        onOpenEditProfile={() => setIsEditProfileOpen(true)}
      />
    </div>
  );
};
