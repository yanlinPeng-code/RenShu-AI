import request from '../request';
import type {
  ApiResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  AdminRegisterRequest,
  AdminLoginRequest,
  AdminResponse
} from '../types';
export const authApi = {
  register: (data: RegisterRequest): Promise<ApiResponse<string>> => {
    return request.post('/api/v1/users/register', data);
  },

  login: (data: LoginRequest): Promise<ApiResponse<AuthResponse>> => {
    return request.post('/api/v1/users/login', data);
  },

  refresh: (refreshToken: string): Promise<ApiResponse<AuthResponse>> => {
    return request.post('/api/v1/users/refresh', { refresh_token: refreshToken });
  },

  getMe: (): Promise<ApiResponse<any>> => {
    return request.get('/api/v1/users/me');
  },

  logout: (): Promise<ApiResponse<null>> => {
    return request.post('/api/v1/users/logout');
  },
};


export  const  adminAuthApi={
        register:(data:AdminRegisterRequest):Promise<ApiResponse<string>> =>{
            return request.post('api/v1/admin/register',data)
        },
        login:(data:AdminLoginRequest):Promise<ApiResponse<AuthResponse>> =>{
            return request.post('api/v1/admin/login',data)

        },
        me: (): Promise<ApiResponse<AdminResponse>> => {
               return request.get('/api/v1/admin/me');
       },

        logout: (): Promise<ApiResponse<null>> => {
                return request.post('/api/v1/admin/logout');
        },
         
    
    
    
    
}
