import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '../types';
import { api, getToken, setToken, removeToken } from '../services/api';
import { signInWithGoogle, signInWithApple } from '../services/socialAuth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: any) => Promise<void>;
  signup: (data: any) => Promise<void>;
  loginAsGuest: () => void;
  loginWithGoogle: () => Promise<void>;
  loginWithGoogleCredential: (credential: string) => Promise<void>;
  loginWithApple: () => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(getToken());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    const currentToken = getToken();
    if (!currentToken) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    if (currentToken === 'demo-guest-token') {
      setUser({
        id: 9999,
        email: 'guest@lokr.ai',
        name: 'Guest Explorer',
        bio: 'Exploring LOKR AI in interactive Demo Mode on GitHub Pages.',
        profile_image: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      setIsLoading(false);
      return;
    }
    try {
      const userData = await api.getMe();
      setUser(userData);
    } catch (err) {
      console.error('Failed to restore user session:', err);
      removeToken();
      setTokenState(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (credentials: any) => {
    const res = await api.login(credentials);
    setToken(res.access_token);
    setTokenState(res.access_token);
    setUser(res.user);
  };

  const signup = async (data: any) => {
    const res = await api.signup(data);
    setToken(res.access_token);
    setTokenState(res.access_token);
    setUser(res.user);
  };

  const loginAsGuest = () => {
    const guestUser: User = {
      id: 9999,
      email: 'guest@lokr.ai',
      name: 'Guest Explorer',
      bio: 'Exploring LOKR AI in interactive Demo Mode on GitHub Pages.',
      profile_image: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    const guestToken = 'demo-guest-token';
    setToken(guestToken);
    setTokenState(guestToken);
    setUser(guestUser);
  };

  const loginWithGoogle = async () => {
    setIsLoading(true);
    try {
      const { access_token } = await signInWithGoogle();
      const res = await api.loginWithGoogle({ access_token });
      setToken(res.access_token);
      setTokenState(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogleCredential = async (credential: string) => {
    setIsLoading(true);
    try {
      const res = await api.loginWithGoogle({ credential });
      setToken(res.access_token);
      setTokenState(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithApple = async () => {
    setIsLoading(true);
    try {
      const appleData = await signInWithApple();
      const res = await api.loginWithApple({
        id_token: appleData.id_token,
        code: appleData.code,
        user: appleData.user,
      });
      setToken(res.access_token);
      setTokenState(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    removeToken();
    setTokenState(null);
    setUser(null);
    const loginPath = `${import.meta.env.BASE_URL}login`;
    window.location.href = loginPath;
  };

  const updateUser = (updated: User) => {
    setUser(updated);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        signup,
        loginAsGuest,
        loginWithGoogle,
        loginWithGoogleCredential,
        loginWithApple,
        logout,
        updateUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
