import React, { useState, useEffect, useRef } from 'react';
import { Camera, Calendar, MessageSquare, Layers, Check, Loader2, AlertCircle } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Avatar } from '../common/Avatar';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { UserStats } from '../../types';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultEditMode?: boolean;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({
  isOpen,
  onClose,
  defaultEditMode = false,
}) => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(defaultEditMode);
  const [name, setName] = useState('');
  const [bio, setBio] = useState('');
  const [stats, setStats] = useState<UserStats>({ conversation_count: 0, message_count: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setIsEditing(defaultEditMode);
  }, [defaultEditMode, isOpen]);

  useEffect(() => {
    if (user) {
      setName(user.name);
      setBio(user.bio || '');
    }
    if (isOpen) {
      loadProfileStats();
      setError(null);
      setSuccess(null);
    }
  }, [isOpen, user]);

  const loadProfileStats = async () => {
    try {
      const data = await api.getProfile();
      setStats(data.stats);
    } catch (err) {
      console.error('Failed to load profile stats:', err);
    }
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingPhoto(true);
    setError(null);

    try {
      const updatedUser = await api.uploadAvatar(file);
      updateUser(updatedUser);
      setSuccess('Profile picture updated successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to upload photo.');
    } finally {
      setIsUploadingPhoto(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name cannot be empty.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const updated = await api.updateProfile({ name: name.trim(), bio: bio.trim() });
      updateUser(updated);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(null), 2500);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? 'Edit Profile' : 'My Profile'}>
      {error && (
        <div className="mb-4 flex items-center gap-2 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs font-medium">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-4 flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-500 text-xs font-medium">
          <Check className="w-4 h-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {isEditing ? (
        <form onSubmit={handleSaveProfile} className="space-y-4">
          {/* Avatar Upload */}
          <div className="flex flex-col items-center mb-6">
            <div className="relative group">
              <Avatar src={user?.profile_image} name={user?.name} size="xl" />
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploadingPhoto}
                className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                title="Change photo"
              >
                {isUploadingPhoto ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  <>
                    <Camera className="w-5 h-5 mb-1" />
                    <span className="text-[10px] font-medium">Upload</span>
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">
              Click photo to change avatar (JPG, PNG, WEBP)
            </p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-1">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-1">
              Bio or Title
            </label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="e.g. Software Engineer, AI Researcher, Student"
              rows={2}
              className="w-full px-3.5 py-2 rounded-xl text-sm bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-white focus:outline-none resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-4 border-t border-neutral-100 dark:border-neutral-800">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 rounded-xl text-xs font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-semibold text-white bg-black hover:bg-neutral-800 dark:bg-white dark:text-black dark:hover:bg-neutral-200 transition-colors disabled:opacity-50"
            >
              {isLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      ) : (
        <div className="space-y-6">
          {/* Top Profile Summary */}
          <div className="flex items-center gap-4">
            <Avatar src={user?.profile_image} name={user?.name} size="lg" />
            <div className="flex-1 min-w-0">
              <h4 className="text-base font-bold text-neutral-900 dark:text-white truncate">
                {user?.name}
              </h4>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                {user?.email}
              </p>
              {user?.bio && (
                <p className="text-xs text-neutral-600 dark:text-neutral-300 mt-1 font-medium">
                  {user.bio}
                </p>
              )}
            </div>
            <button
              onClick={() => setIsEditing(true)}
              type="button"
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-neutral-900 dark:text-white bg-neutral-100 dark:bg-[#252525] hover:bg-neutral-200 dark:hover:bg-[#303030] transition-colors shrink-0"
            >
              Edit
            </button>
          </div>

          {/* Account Metrics Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-2xl bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800">
              <div className="flex items-center gap-2 text-xs text-neutral-500 dark:text-neutral-400 mb-1">
                <MessageSquare className="w-4 h-4 text-neutral-500" />
                <span>Conversations</span>
              </div>
              <p className="text-xl font-bold text-neutral-900 dark:text-white">
                {stats.conversation_count}
              </p>
            </div>

            <div className="p-3.5 rounded-2xl bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-800">
              <div className="flex items-center gap-2 text-xs text-neutral-500 dark:text-neutral-400 mb-1">
                <Layers className="w-4 h-4 text-neutral-500" />
                <span>Messages Sent</span>
              </div>
              <p className="text-xl font-bold text-neutral-900 dark:text-white">
                {stats.message_count}
              </p>
            </div>
          </div>

          {/* Account Details Info */}
          <div className="p-4 rounded-2xl bg-neutral-50/80 dark:bg-[#212121]/60 border border-neutral-200 dark:border-neutral-800 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-neutral-400" />
                <span>Member Since</span>
              </span>
              <span className="font-medium text-neutral-900 dark:text-white">
                {formatDate(user?.created_at)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-neutral-500 dark:text-neutral-400">Account Status</span>
              <span className="inline-flex items-center gap-1 font-semibold text-emerald-500">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Active
              </span>
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
};
