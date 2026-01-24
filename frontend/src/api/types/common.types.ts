// API 通用响应类型
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  request_id?: string;
  host_id?: string;
  success?: boolean;
}
