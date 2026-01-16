import { AIModelConfig } from './chat.types';
// 专业视图枚举
export enum ProView {
  DIAGNOSIS = 'DIAGNOSIS',
  REPORTS = 'REPORTS'
}
export const AVAILABLE_MODELS: AIModelConfig[] = [
  { id: 'gemini-3-flash-preview', name: 'Gemini 3.0 Flash', description: 'Fast & Efficient', supportsThinking: true, supportsVision: true },
  { id: 'gemini-3-pro-preview', name: 'Gemini 3.0 Pro', description: 'Complex Reasoning', supportsThinking: true, supportsVision: true },
  { id: 'gemini-2.5-flash-latest', name: 'Gemini 2.5 Flash', description: 'Balanced', supportsThinking: true, supportsVision: true },
];