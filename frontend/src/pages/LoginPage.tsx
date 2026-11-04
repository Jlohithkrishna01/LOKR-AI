import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2, AlertCircle, ArrowRight, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Logo } from '../components/common/Logo';
import { ThemeToggle } from '../components/common/ThemeToggle';
import { initGoogleOneTap } from '../services/socialAuth';

export const LoginPage: React.FC = () => {
  const { login, loginAsGuest, loginWithGoogle, loginWithGoogleCredential, loginWithApple } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isAppleLoading, setIsAppleLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAnyLoading = isLoading || isGoogleLoading || isAppleLoading;

  // Initialize official Google One Tap account selector
  useEffect(() => {
    initGoogleOneTap(
      async (credential) => {
        setIsGoogleLoading(true);
        setError(null);
        try {
          await loginWithGoogleCredential(credential);
          navigate('/');
        } catch (err: any) {
          setError(err.message || 'Google authentication failed. Please try again.');
        } finally {
          setIsGoogleLoading(false);
        }
      },
      (err) => {
        console.debug('Google One Tap notice:', err);
      }
    );
  }, [loginWithGoogleCredential, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await login({
        email: email.trim(),
        password,
        remember_me: rememberMe,
      });
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    setError(null);
    try {
      await loginWithGoogle();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Google sign in failed. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleAppleLogin = async () => {
    setIsAppleLoading(true);
    setError(null);
    try {
      await loginWithApple();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Apple sign in failed. Please try again.');
    } finally {
      setIsAppleLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-4 py-8 bg-white dark:bg-[#0d0d0d] transition-colors relative">
      {/* Top Bar Theme Toggle */}
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-8 text-center">
          <Logo size="lg" className="mb-3" />
          <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white tracking-tight">
            Welcome back
          </h2>
          <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
            Sign in to continue to LOKR AI
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-white dark:bg-[#181818] rounded-3xl p-6 sm:p-8 border border-neutral-200 dark:border-neutral-800 shadow-lg shadow-neutral-200/50 dark:shadow-none">
          {error && (
            <div
              role="alert"
              className="mb-5 flex items-center gap-2.5 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs font-medium animate-in fade-in"
            >
              <AlertCircle className="w-4 h-4 shrink-0" aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          {/* Modern Social Login Options: Google & Apple */}
          <div className="flex flex-col gap-3 mb-6">
            {/* 1. Continue with Google */}
            <button
              type="button"
              disabled={isAnyLoading}
              onClick={handleGoogleLogin}
              aria-label="Continue with Google"
              aria-busy={isGoogleLoading}
              className="w-full flex items-center justify-center gap-3 h-11 px-4 rounded-xl bg-white text-neutral-800 border border-neutral-300 dark:border-neutral-700 dark:bg-[#181818] dark:text-neutral-100 hover:bg-neutral-50 dark:hover:bg-neutral-800 active:bg-neutral-100 active:scale-[0.99] font-medium text-sm shadow-sm transition-all disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-neutral-400"
            >
              {isGoogleLoading ? (
                <Loader2 className="w-4 h-4 animate-spin text-neutral-600 dark:text-neutral-300" aria-hidden="true" />
              ) : (
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
              )}
              <span>{isGoogleLoading ? 'Connecting to Google...' : 'Continue with Google'}</span>
            </button>

            {/* 2. Continue with Apple */}
            <button
              type="button"
              disabled={isAnyLoading}
              onClick={handleAppleLogin}
              aria-label="Continue with Apple"
              aria-busy={isAppleLoading}
              className="w-full flex items-center justify-center gap-3 h-11 px-4 rounded-xl bg-black text-white border border-black hover:bg-neutral-900 active:bg-neutral-950 dark:bg-white dark:text-black dark:border-white dark:hover:bg-neutral-200 active:scale-[0.99] font-medium text-sm shadow-sm transition-all disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-neutral-400"
            >
              {isAppleLoading ? (
                <Loader2 className="w-4 h-4 animate-spin text-white dark:text-black" aria-hidden="true" />
              ) : (
                <svg className="w-4 h-4 shrink-0 fill-current text-white dark:text-black" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.38c.62-.75 1.04-1.8 0.93-2.85-.9.04-1.99.6-2.63 1.35-.57.65-1.07 1.72-.93 2.74 1 .08 2.02-.51 2.63-1.24z" />
                </svg>
              )}
              <span>{isAppleLoading ? 'Connecting to Apple...' : 'Continue with Apple'}</span>
            </button>
          </div>

          {/* Divider: ──────── OR ──────── */}
          <div className="relative my-6" role="separator" aria-label="Or continue with email">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-neutral-200 dark:border-neutral-800" />
            </div>
            <div className="relative flex justify-center text-xs uppercase tracking-wider font-semibold">
              <span className="bg-white dark:bg-[#181818] px-3 text-neutral-400 dark:text-neutral-500">
                OR
              </span>
            </div>
          </div>

          {/* Email / Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isAnyLoading}
                autoComplete="email"
                placeholder="name@example.com"
                className="w-full px-4 py-2.5 rounded-xl text-sm bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none transition-colors disabled:opacity-50"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs font-medium text-neutral-600 dark:text-neutral-400 hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isAnyLoading}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="w-full pl-4 pr-11 py-2.5 rounded-xl text-sm bg-neutral-50 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none transition-colors disabled:opacity-50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
                  tabIndex={-1}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none text-xs text-neutral-600 dark:text-neutral-300">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  disabled={isAnyLoading}
                  className="w-4 h-4 rounded text-neutral-900 dark:text-white border-neutral-300 dark:border-neutral-700"
                />
                <span>Remember me on this device</span>
              </label>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={isAnyLoading}
              className="w-full flex items-center justify-center gap-2 mt-4 px-4 py-3 rounded-xl bg-black text-white hover:bg-neutral-800 dark:bg-white dark:text-black dark:hover:bg-neutral-200 font-semibold text-sm shadow-sm transition-all disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Guest / Demo Mode Button */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-neutral-200 dark:border-neutral-800" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white dark:bg-[#181818] px-2.5 text-neutral-400 font-medium">
                Or explore without backend
              </span>
            </div>
          </div>

          <button
            type="button"
            disabled={isAnyLoading}
            onClick={() => {
              loginAsGuest();
              navigate('/');
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-neutral-100/60 dark:bg-[#222222] hover:bg-neutral-200/60 dark:hover:bg-[#2a2a2a] text-neutral-800 dark:text-neutral-200 font-medium text-xs transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
            <span>Try Demo Mode (Instant Browser Access)</span>
          </button>

          {/* Footer Link */}
          <div className="mt-6 text-center text-xs text-neutral-500 dark:text-neutral-400">
            Don't have an account?{' '}
            <Link
              to="/signup"
              className="font-semibold text-neutral-900 dark:text-white hover:underline"
            >
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
