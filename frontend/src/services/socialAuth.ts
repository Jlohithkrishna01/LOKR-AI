// ============================================================================
// LOKR AI - Social Authentication Service (Google Identity Services & Apple ID)
// ============================================================================

declare global {
  interface Window {
    google?: {
      accounts: {
        oauth2: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            prompt?: string;
            callback: (response: { access_token?: string; error?: string; error_description?: string }) => void;
            error_callback?: (err: { type: string; message?: string }) => void;
          }) => {
            requestAccessToken: (options?: { prompt?: string }) => void;
          };
        };
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential?: string; select_by?: string }) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
            context?: string;
          }) => void;
          prompt: (notification?: (notification: {
            isNotDisplayed: () => boolean;
            isSkippedMoment: () => boolean;
            isDismissedMoment: () => boolean;
            getNotDisplayedReason: () => string;
            getSkippedReason: () => string;
            getDismissedReason: () => string;
          }) => void) => void;
          renderButton?: (parent: HTMLElement, options: any) => void;
          cancel?: () => void;
        };
      };
    };
    AppleID?: {
      auth: {
        init: (config: {
          clientId: string;
          scope: string;
          redirectURI: string;
          state?: string;
          nonce?: string;
          usePopup: boolean;
        }) => void;
        signIn: () => Promise<{
          authorization: {
            code: string;
            id_token: string;
            state?: string;
          };
          user?: {
            name?: {
              firstName?: string;
              lastName?: string;
            };
            email?: string;
          };
        }>;
      };
    };
  }
}

const GOOGLE_SDK_URL = 'https://accounts.google.com/gsi/client';
const APPLE_SDK_URL = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js';

let googleSdkPromise: Promise<void> | null = null;
let appleSdkPromise: Promise<void> | null = null;

/**
 * Dynamically loads an external JavaScript library with a timeout and caching.
 */
function loadScript(src: string, id: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const existing = document.getElementById(id) as HTMLScriptElement | null;
    if (existing) {
      if ((existing as any).dataset?.loaded === 'true') {
        resolve();
        return;
      }
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => reject(new Error(`Failed to load ${src}`)), { once: true });
      return;
    }

    const script = document.createElement('script');
    script.id = id;
    script.src = src;
    script.async = true;
    script.defer = true;

    const timeout = setTimeout(() => {
      reject(new Error(`Timed out loading authentication library: ${src}`));
    }, 15000);

    script.onload = () => {
      clearTimeout(timeout);
      (script as any).dataset.loaded = 'true';
      resolve();
    };

    script.onerror = () => {
      clearTimeout(timeout);
      reject(new Error(`Failed to load authentication library from ${src}. Please check your connection or ad blocker.`));
    };

    document.head.appendChild(script);
  });
}

/**
 * Ensures Google Identity Services SDK is loaded and ready.
 */
export async function loadGoogleSDK(): Promise<void> {
  if (typeof window !== 'undefined' && window.google?.accounts?.oauth2 && window.google?.accounts?.id) {
    return;
  }
  if (!googleSdkPromise) {
    googleSdkPromise = loadScript(GOOGLE_SDK_URL, 'google-gsi-script').then(async () => {
      // Poll briefly if window.google is not yet initialized
      for (let i = 0; i < 20; i++) {
        if (window.google?.accounts?.oauth2) break;
        await new Promise((r) => setTimeout(r, 50));
      }
    });
  }
  return googleSdkPromise;
}

/**
 * Ensures Apple Sign in with Apple SDK is loaded and ready.
 */
export async function loadAppleSDK(): Promise<void> {
  if (typeof window !== 'undefined' && window.AppleID?.auth) {
    return;
  }
  if (!appleSdkPromise) {
    appleSdkPromise = loadScript(APPLE_SDK_URL, 'apple-id-script').then(async () => {
      for (let i = 0; i < 20; i++) {
        if (window.AppleID?.auth) break;
        await new Promise((r) => setTimeout(r, 50));
      }
    });
  }
  return appleSdkPromise;
}

// Automatically preload SDKs in background on page load
if (typeof window !== 'undefined') {
  loadGoogleSDK().catch(() => {});
  loadAppleSDK().catch(() => {});
}

/**
 * Helper to generate secure random strings for OAuth state/nonce.
 */
function generateRandomString(length: number = 32): string {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const array = new Uint8Array(length);
  if (typeof window !== 'undefined' && window.crypto) {
    window.crypto.getRandomValues(array);
    return Array.from(array, (b) => charset[b % charset.length]).join('');
  }
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

/**
 * Initializes Google One Tap / FedCM account picker.
 * Displays signed-in Google accounts on screen with avatar, name, and email.
 */
export async function initGoogleOneTap(
  onCredentialReceived: (credential: string) => Promise<void> | void,
  onError?: (err: Error) => void
): Promise<void> {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  if (!clientId || clientId.trim() === '' || clientId.includes('your_google_client_id')) {
    return;
  }

  try {
    await loadGoogleSDK();
    if (!window.google?.accounts?.id) return;

    window.google.accounts.id.initialize({
      client_id: clientId.trim(),
      callback: (res) => {
        if (res.credential) {
          onCredentialReceived(res.credential);
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
      context: 'signin',
    });

    window.google.accounts.id.prompt((notification) => {
      if (notification.isNotDisplayed()) {
        const reason = notification.getNotDisplayedReason();
        console.debug('Google One Tap not displayed:', reason);
      }
    });
  } catch (err: any) {
    onError?.(err);
  }
}

/**
 * Initiates the official Google Identity Services OAuth 2.0 Account Chooser popup flow.
 * Forces Google to present the official account selection dialog listing all signed-in
 * Google profiles (avatar, full name, email address) and "Use another account".
 * Returns the Google access_token to be validated securely on the backend.
 */
export async function signInWithGoogle(): Promise<{ access_token: string }> {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  if (!clientId || clientId.trim() === '' || clientId.includes('your_google_client_id')) {
    throw new Error(
      'Google Client ID is not configured. Please set VITE_GOOGLE_CLIENT_ID in your frontend .env file.'
    );
  }

  await loadGoogleSDK();

  const google = window.google;
  if (!google?.accounts?.oauth2) {
    throw new Error('Google Sign-In SDK is unavailable. Please check your network connection or ad blocker.');
  }

  return new Promise((resolve, reject) => {
    let hasResolved = false;

    try {
      const client = google.accounts.oauth2.initTokenClient({
        client_id: clientId.trim(),
        scope: 'openid email profile',
        prompt: 'select_account', // CRITICAL: forces Google to display account selection with avatars and emails
        callback: (response) => {
          hasResolved = true;
          if (response.error) {
            if (response.error === 'access_denied') {
              reject(new Error('Google sign-in was cancelled.'));
            } else {
              reject(new Error(response.error_description || `Google sign-in error: ${response.error}`));
            }
            return;
          }
          if (!response.access_token) {
            reject(new Error('No access token received from Google authentication.'));
            return;
          }
          resolve({ access_token: response.access_token });
        },
        error_callback: (err) => {
          hasResolved = true;
          if (err.type === 'popup_closed') {
            reject(new Error('Google sign-in window was closed.'));
          } else if (err.type === 'popup_failed_to_open') {
            reject(new Error('Google sign-in popup was blocked by your browser. Please allow popups for this site.'));
          } else {
            reject(new Error(err.message || 'An error occurred during Google sign-in.'));
          }
        },
      });

      // Synchronously request access token with prompt 'select_account'
      client.requestAccessToken({ prompt: 'select_account' });
    } catch (err: any) {
      if (!hasResolved) {
        reject(new Error(err.message || 'Could not initiate Google authentication popup.'));
      }
    }
  });
}

/**
 * Initiates the official Apple Sign in with Apple popup flow.
 * Returns the Apple id_token, code, and user details to be validated securely on the backend.
 */
export async function signInWithApple(): Promise<{
  id_token: string;
  code?: string;
  user?: any;
}> {
  const clientId = import.meta.env.VITE_APPLE_CLIENT_ID;

  if (!clientId || clientId.trim() === '' || clientId.includes('your_apple_service_id')) {
    throw new Error(
      'Apple Client ID is not configured. Please set VITE_APPLE_CLIENT_ID in your frontend .env file.'
    );
  }

  await loadAppleSDK();

  const apple = window.AppleID;
  if (!apple?.auth) {
    throw new Error('Apple Sign-In SDK is unavailable. Please check your network connection.');
  }

  try {
    const state = generateRandomString(24);
    const nonce = generateRandomString(24);

    sessionStorage.setItem('apple_auth_state', state);
    sessionStorage.setItem('apple_auth_nonce', nonce);

    const configuredRedirect = import.meta.env.VITE_APPLE_REDIRECT_URI;
    const redirectURI = configuredRedirect && configuredRedirect.trim()
      ? configuredRedirect.trim()
      : window.location.origin;

    apple.auth.init({
      clientId: clientId.trim(),
      scope: 'name email',
      redirectURI,
      state,
      nonce,
      usePopup: true,
    });

    const response = await apple.auth.signIn();

    if (!response?.authorization?.id_token) {
      throw new Error('No identity token returned from Apple.');
    }

    return {
      id_token: response.authorization.id_token,
      code: response.authorization.code,
      user: response.user,
    };
  } catch (err: any) {
    if (err.error === 'popup_closed_by_user') {
      throw new Error('Apple sign-in was cancelled.');
    }
    if (err.error === 'popup_blocked') {
      throw new Error('Apple sign-in popup was blocked by your browser. Please allow popups for this site.');
    }
    throw new Error(err.error || err.message || 'Failed to authenticate with Apple.');
  }
}
