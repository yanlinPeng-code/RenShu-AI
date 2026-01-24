// 用户认证请求
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

export interface RefreshRequest {
  refresh_token: string;
}

// 管理员认证请求
export interface AdminLoginRequest {
  username: string;
  password: string;
}

export interface AdminRegisterRequest {
  username: string;
  password: string;
}

// 认证响应
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user_id: string;
}

export interface AdminResponse {
  id: string;
  username: string;
  role: string;
  avatar_url?: string;
  is_active?: boolean;
  created_at?: Date;
}
