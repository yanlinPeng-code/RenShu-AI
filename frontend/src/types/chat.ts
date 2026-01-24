// 聊天消息
export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
  attachments?: Array<{
    type: 'image' | 'file';
    url: string;
    name: string;
  }>;
}
// AI 模型配置
export interface AIModelConfig {
  id: string;
  name: string;
  description: string;
  supportsThinking: boolean;
  supportsVision: boolean;
  provider: 'google' | 'openai' | 'anthropic' | 'qwen';
  contextWindow?: string; // e.g. "128K"
  cost?: string; // e.g. "$$$"
}

// 用户自定义模型配置存储结构 (Deprecated in favor of ProviderConfig for keys, but kept for legacy/custom models if needed)
export interface UserRuntimeConfig {
  apiKey: string;
  baseUrl?: string;
}

// 新：提供商级别的配置
export interface ProviderConfig {
  apiKey: string;
  baseUrl?: string;
  enabled: boolean;
}

// 新：自定义模型定义
export interface CustomModel extends AIModelConfig {
  isCustom: true;
}
