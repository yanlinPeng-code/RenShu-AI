// API通用响应类型
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  request_id?: string;
  host_id?: string;
  success?: boolean;
}



// 认证相关请求/响应类型
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: 'patient' | 'doctor';
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user_id: string;
}

export interface RefreshRequest {
  refresh_token: string;
}
