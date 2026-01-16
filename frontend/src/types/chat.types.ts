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

// AI模型配置
export interface AIModelConfig {
  id: string;
  name: string;
  description: string;
  supportsThinking: boolean;
  supportsVision: boolean;
}
