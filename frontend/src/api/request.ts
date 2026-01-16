import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { convertKeysToSnake } from '../utils/camelToSnakeConverter';

// 根据环境选择API基础URL
const getBaseURL = (): string => {
  if (import.meta.env.PROD) {
    // 生产环境 - 云服务器地址，请根据实际部署地址修改
    return import.meta.env.VITE_API_BASE_URL || 'https://your-production-server.com';
  }
  // 开发环境 - 本地后端
  return 'http://localhost:8000';
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
    const token = localStorage.getItem('access_token');
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
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${getBaseURL()}/api/v1/users/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = convertKeysToSnake(res.data).data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          // 重试原请求
          error.config.headers.Authorization = `Bearer ${access_token}`;
          return request(error.config);
        } catch {
          // 刷新失败，清除token
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default request;
