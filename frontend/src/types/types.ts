export enum UserRole {
  PUBLIC = 'PUBLIC',
  PROFESSIONAL = 'PROFESSIONAL'
}

export interface UserPersona {
  age: string;
  gender: string;
  chiefComplaint: string; // 主诉
  medicalHistory: string; // 病史
  suspectedDiagnosis: string; // 可疑的诊断
  contraindications: string; // 禁忌项
  recommendedTreatment: string; // 推荐的治疗手段
}

export interface User {
  id: string;
  name: string;
  role: UserRole;
  avatar: string;
  specialty?: string; // For doctors
  healthScore?: number; // For patients
  persona?: UserPersona; // Structured medical profile
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
  attachments?: Array<{type: 'image' | 'file', url: string, name: string}>;
}

export enum ProView {
  DIAGNOSIS = 'DIAGNOSIS',
  REPORTS = 'REPORTS'
}

export interface AIModelConfig {
  id: string;
  name: string;
  description: string;
  supportsThinking: boolean;
  supportsVision: boolean;
}

export const AVAILABLE_MODELS: AIModelConfig[] = [
  { id: 'gemini-3-flash-preview', name: 'Gemini 3.0 Flash', description: 'Fast & Efficient', supportsThinking: true, supportsVision: true },
  { id: 'gemini-3-pro-preview', name: 'Gemini 3.0 Pro', description: 'Complex Reasoning', supportsThinking: true, supportsVision: true },
  { id: 'gemini-2.5-flash-latest', name: 'Gemini 2.5 Flash', description: 'Balanced', supportsThinking: true, supportsVision: true },
];