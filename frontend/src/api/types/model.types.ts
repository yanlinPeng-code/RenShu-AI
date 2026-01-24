// 管理员：模型供应商管理
export interface ModelProviderCreate {
  name?: string;
  label?: string;
  description?: string;
  icon?: string;
  base_url?: string;
  api_key?: string;
  supported_model_types?: string[];
  position?: number;
}

export interface ModelProviderUpdate {
  provider_id?: string;
  label?: string;
  description?: string;
  icon?: string;
  icon_background?: string;
  base_url?: string;
  api_key?: string;
  supported_model_types?: string[];
  help_url?: string;
  is_enabled?: boolean;
  position?: number;
}

export interface ModelProviderDelete {
  provider_id?: string;
}

// 管理员：模型配置管理
export interface ModelConfigCreate {
  provider_id?: string;
  model_name?: string;
  label?: string; // Add label field
  description?: string;
  model_type?: string;
  features?: string[];
  context_window?: number;
  default_temperature?: number;
  default_top_p?: number;
  default_max_tokens?: number;
  default_parameters?: any;
  position?: number;
}

export interface ModelConfigUpdate {
  model_config_id?: string;
  label?: string;
  description?: string;
  model_type?: string;
  features?: string[];
  context_window?: number;
  max_output_tokens?: number;
  default_temperature?: number;
  default_top_p?: number;
  default_max_tokens?: number;
  default_parameters?: any;
  attributes?: any;
  pricing?: any;
  is_enabled?: boolean;
  position?: number;
}

export interface ModelConfigDelete {
  model_config_id?: string;
}

export interface ProviderApiKeyVerify {
  provider_id?: string;
  api_key?: string;
  base_url?: string;
  model_name?: string;
}

// // 用户：模型配置管理
// export interface UserModelConfigCreate {
//   provider_id?: string;
//   model_config_id?: string;
//   custom_model_name?: string;
//   api_key?: string;
//   base_url?: string;
//   custom_temperature?: number;
//   custom_top_p?: number;
//   custom_max_tokens?: number;
//   custom_parameters?: any;
//   alias?: string;
//   is_default?: boolean;
// }

// export interface UserModelConfigUpdate {
//   model_config_id?: string;
//   custom_model_name?: string;
//   api_key?: string;
//   base_url?: string;
//   custom_temperature?: number;
//   custom_top_p?: number;
//   custom_max_tokens?: number;
//   custom_parameters?: any;
//   alias?: string;
//   is_default?: boolean;
//   is_enabled?: boolean;
// }
