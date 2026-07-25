export type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type?: string;
};

export type AuthSession = {
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
    is_active: boolean;
    email_verified: boolean;
    avatar_url?: string | null;
    email_verified_at?: string | null;
    last_login_at?: string | null;
  };
  tokens: AuthTokens;
};

const AUTH_SESSION_KEY = "loop.auth.session";
const ACCESS_TOKEN_KEY = "loop.auth.access_token";
const REFRESH_TOKEN_KEY = "loop.auth.refresh_token";

function canUseStorage() {
  return typeof window !== "undefined";
}

export function saveAuthSession(session: AuthSession) {
  if (!canUseStorage()) return;
  window.localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(session));
  window.localStorage.setItem(ACCESS_TOKEN_KEY, session.tokens.access_token);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, session.tokens.refresh_token);
}

export function getAuthSession(): AuthSession | null {
  if (!canUseStorage()) return null;
  const rawSession = window.localStorage.getItem(AUTH_SESSION_KEY);
  if (!rawSession) return null;

  try {
    return JSON.parse(rawSession) as AuthSession;
  } catch {
    return null;
  }
}

export function getAccessToken(): string | null {
  if (!canUseStorage()) return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (!canUseStorage()) return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function hasAuthSession(): boolean {
  return Boolean(getAccessToken() && getRefreshToken());
}

export function clearAuthSession() {
  if (!canUseStorage()) return;
  window.localStorage.removeItem(AUTH_SESSION_KEY);
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}
