import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { convertKeysToSnake } from '../utils/camelToSnakeConverter';

// 根据环境选择API基础URL
const getBaseURL = (): string => {
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_BASE_URL || 'https://your-production-server.com';
  }
  return 'http://localhost:8000';
};

// Token 刷新状态管理
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

// 添加等待刷新的请求到队列
const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

// 刷新完成后，通知所有等待的请求
const onTokenRefreshed = (newToken: string) => {
  refreshSubscribers.forEach(callback => callback(newToken));
  refreshSubscribers = [];
};

// 根据当前路由判断应该使用哪个角色的 token
const getTokenPrefix = (): string => {
    const pathname = window.location.pathname;
    if (pathname.startsWith('/admin') || pathname.startsWith('/login/admin') || pathname.startsWith('/register/admin')) {
        return 'admin_';
    }
    if (pathname.startsWith('/professional') || pathname.startsWith('/login/professional') || pathname.startsWith('/register/professional')) {
        return 'professional_';
    }
    return 'user_';
};

// 清除认证数据并跳转到登录页
const handleAuthFailure = () => {
    const prefix = getTokenPrefix();
    const savedUser = localStorage.getItem(`${prefix}user`);
    let isAdmin = false;

    try {
        if (savedUser) {
            const user = JSON.parse(savedUser);
            isAdmin = user.role === 'ADMIN';
        }
    } catch {}

    // 清除当前角色的认证数据
    localStorage.removeItem(`${prefix}access_token`);
    localStorage.removeItem(`${prefix}refresh_token`);
    localStorage.removeItem(`${prefix}user_id`);
    localStorage.removeItem(`${prefix}user`);

    // 根据用户类型跳转到对应的登录页
    window.location.href = isAdmin ? '/login/admin' : '/';
};

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const prefix = getTokenPrefix();
    const token = localStorage.getItem(`${prefix}access_token`);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => convertKeysToSnake(response.data),

  async (error) => {
    const originalRequest = error.config;

    // 如果不是 401 错误，直接返回
    if (error.response?.status !== 401) {
      return Promise.reject(error);
    }

    // 如果是刷新 token 的请求失败，直接跳转登录页
    if (originalRequest.url?.includes('/refresh')) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    // 如果已经重试过，不再重试
    if (originalRequest._retry) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem(`${getTokenPrefix()}refresh_token`);
    if (!refreshToken) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    // 标记该请求已重试
    originalRequest._retry = true;

    // 如果正在刷新 token，将请求加入队列等待
    if (isRefreshing) {
      return new Promise((resolve) => {
        subscribeTokenRefresh((newToken: string) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          resolve(request(originalRequest));
        });
      });
    }

    // 开始刷新 token
    isRefreshing = true;

    try {
      const res = await axios.post(`${getBaseURL()}/api/v1/users/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token: newRefreshToken } = convertKeysToSnake(res.data).data;

      // 保存新的 token（使用角色前缀）
      const prefix = getTokenPrefix();
      localStorage.setItem(`${prefix}access_token`, access_token);
      localStorage.setItem(`${prefix}refresh_token`, newRefreshToken);

      // 通知所有等待的请求
      onTokenRefreshed(access_token);

      // 重试原请求
      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return request(originalRequest);

    } catch (refreshError) {
      // 刷新失败，跳转登录页
      handleAuthFailure();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default request;
