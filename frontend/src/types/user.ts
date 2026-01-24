// 用户角色枚举
export enum UserRole {
  PUBLIC = 'PUBLIC',
  PROFESSIONAL = 'PROFESSIONAL',
  ADMIN = 'ADMIN'
}

// 用户画像
export interface UserPersona {
  age: string;
  gender: string;
  chiefComplaint: string;
  medicalHistory: string;
  suspectedDiagnosis: string;
  contraindications: string;
  recommendedTreatment: string;
}

// 用户信息
export interface User {
  id: string;
  name: string;
  role: UserRole;
  avatar: string;
  specialty?: string;
  healthScore?: number;
  persona?: UserPersona;
}
