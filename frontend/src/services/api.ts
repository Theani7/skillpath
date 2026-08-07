import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

export type SkipAuthRedirectConfig = InternalAxiosRequestConfig & { _skipAuthRedirect?: boolean };

let logoutHandler: (() => void) | null = null;
export const registerLogoutHandler = (fn: () => void) => { logoutHandler = fn; };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = (error.config || {}) as SkipAuthRedirectConfig;
    const status = error.response?.status;
    const url = config.url || '';
    const skipRedirect = config._skipAuthRedirect;
    const isAuthMe = url.includes('/auth/me');

    if (status === 401 && !isAuthMe && !skipRedirect) {
      // Clearing auth state re-renders the protected routes, which redirect to "/".
      // Do not touch window.history here - React Router owns navigation.
      if (logoutHandler) {
        logoutHandler();
      }
    }
    return Promise.reject(error);
  },
);

export default api;
