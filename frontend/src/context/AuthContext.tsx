/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useCallback, useMemo, type ReactNode } from 'react';
import api, { registerLogoutHandler, type SkipAuthRedirectConfig } from '../services/api';
import type { AuthUser } from '../types';

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: () => Promise<AuthUser | null>;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<AuthUser>) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

const PROFILE_CACHE_KEY = 'skillpath_profile';

const writeProfile = (profile: AuthUser) => {
  try { localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(profile)); } catch { /* noop */ }
};
const clearProfile = () => {
  try { localStorage.removeItem(PROFILE_CACHE_KEY); } catch { /* noop */ }
};
const readProfile = (): AuthUser | null => {
  try { return JSON.parse(localStorage.getItem(PROFILE_CACHE_KEY) || 'null') as AuthUser | null; } catch { return null; }
};

const buildProfile = (data: { role: string; username: string; full_name: string; email: string | null }): AuthUser => ({
  role: data.role as AuthUser['role'],
  username: data.username,
  full_name: data.full_name,
  email: data.email,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(() => readProfile());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const handleOAuthRedirect = () => {
      const params = new URLSearchParams(window.location.search);
      const oauthToken = params.get('oauth_token');
      const oauthRefresh = params.get('oauth_refresh');
      if (oauthToken && oauthRefresh) {
        document.cookie = `skillpath_access=${oauthToken}; path=/; max-age=1800`;
        document.cookie = `skillpath_refresh=${oauthRefresh}; path=/api/auth; max-age=2592000`;
        params.delete('oauth_token');
        params.delete('oauth_refresh');
        const newUrl = window.location.pathname + (params.toString() ? `?${params.toString()}` : '');
        window.history.replaceState({}, '', newUrl);
      }
    };

    const fetchUser = async () => {
      try {
        const res = await api.get('/api/auth/me', { _skipAuthRedirect: true } as SkipAuthRedirectConfig);
        if (!cancelled) {
          const profile = buildProfile(res.data);
          setUser(profile);
          writeProfile(profile);
        }
      } catch (_err) {
        if (!cancelled) {
          setUser(null);
          clearProfile();
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    handleOAuthRedirect();
    fetchUser();
    return () => { cancelled = true; };
  }, []);

  const login = useCallback(async (): Promise<AuthUser | null> => {
    try {
      const res = await api.get('/api/auth/me', { _skipAuthRedirect: true } as SkipAuthRedirectConfig);
      const profile = buildProfile(res.data);
      setUser(profile);
      writeProfile(profile);
      return profile;
    } catch (_err) {
      setUser(null);
      clearProfile();
      return null;
    }
  }, []);

  const updateUser = useCallback((updates: Partial<AuthUser>) => {
    setUser((prev) => {
      const next = prev ? { ...prev, ...updates } : prev;
      if (next) writeProfile(next);
      return next;
    });
  }, []);

  const logout = useCallback(async () => {
    try { await api.post('/api/auth/logout'); } catch { /* noop */ }
    setUser(null);
    clearProfile();
  }, []);

  useEffect(() => {
    registerLogoutHandler(() => {
      setUser(null);
      clearProfile();
    });
  }, []);

  const value = useMemo(() => ({ user, loading, login, logout, updateUser }), [user, loading, login, logout, updateUser]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
