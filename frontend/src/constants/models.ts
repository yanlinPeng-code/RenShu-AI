import { AIModelConfig } from '../types';

export const AVAILABLE_MODELS: AIModelConfig[] = [
  // Google
  { id: 'gemini-3-flash-preview', name: 'Gemini 3.0 Flash', description: '极速、智能的下一代模型', supportsThinking: true, supportsVision: true, provider: 'google' },
  { id: 'gemini-3-pro-preview', name: 'Gemini 3.0 Pro', description: '强大的多模态推理能力', supportsThinking: true, supportsVision: true, provider: 'google' },
  { id: 'gemini-2.5-flash-latest', name: 'Gemini 2.5 Flash', description: '性能平衡的经典之选', supportsThinking: true, supportsVision: true, provider: 'google' },

  // OpenAI
  { id: 'gpt-4o', name: 'GPT-4o', description: 'OpenAI 旗舰全能模型', supportsThinking: false, supportsVision: true, provider: 'openai' },
  { id: 'gpt-4o-mini', name: 'GPT-4o-mini', description: '高效、轻量的小模型', supportsThinking: false, supportsVision: true, provider: 'openai' },
  { id: 'o1-preview', name: 'o1-preview', description: '擅长复杂逻辑推理', supportsThinking: true, supportsVision: false, provider: 'openai' },

  // Anthropic
  { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', description: '最智能的 Claude 模型', supportsThinking: false, supportsVision: true, provider: 'anthropic' },
  { id: 'claude-3-opus', name: 'Claude 3 Opus', description: '深度思考与长文本处理', supportsThinking: false, supportsVision: true, provider: 'anthropic' },

  // Qwen (阿里千问)
  { id: 'qwen-max', name: '通义千问-Max', description: '阿里最强商用模型', supportsThinking: false, supportsVision: true, provider: 'qwen' },
  { id: 'qwen-plus', name: '通义千问-Plus', description: '能力全面提升', supportsThinking: false, supportsVision: true, provider: 'qwen' },
  { id: 'qwen-turbo', name: '通义千问-Turbo', description: '极速响应', supportsThinking: false, supportsVision: false, provider: 'qwen' },
];

export const PROVIDERS = [
  { id: 'google', name: 'Google Gemini', icon: '🤖' },
  { id: 'openai', name: 'OpenAI GPT', icon: '🚀' },
  { id: 'anthropic', name: 'Anthropic Claude', icon: '🎨' },
  { id: 'qwen', name: 'AliCloud Qwen', icon: '☁️' },
];

// 模型类型分类（8大类）
export const MODEL_TYPE_CATEGORIES = [
  { key: 'all', label: '全部' },
  { key: 'llm', label: 'LLM' },
  { key: 'multimodal', label: '多模态' },
  { key: 'embedding', label: '嵌入' },
  { key: 'rerank', label: '重排序' },
  { key: 'image', label: '图像' },
  { key: 'audio', label: '音频' },
  { key: 'video', label: '视频' },
  { key: 'code', label: '代码' }
];

// 供应商支持的模型类型
export const SUPPORTED_MODEL_TYPES = [
  { id: 'llm', label: 'LLM' },
  { id: 'multimodal', label: '多模态' },
  { id: 'embedding', label: '嵌入' },
  { id: 'rerank', label: '重排序' },
  { id: 'image', label: '图像' },
  { id: 'audio', label: '音频' },
  { id: 'video', label: '视频' },
  { id: 'code', label: '代码' },
];

// 模型配置类型（用于表单）
export const MODEL_CONFIG_TYPES = [
    'LLM (大语言模型)',
    'Multimodal (多模态)',
    'Embedding (文本嵌入)',
    'Image (图像生成)',
    'Code (代码大模型)'
];

// 模型特性
export const MODEL_FEATURES = [
    { id: 'structured', label: '结构化输出' },
    { id: 'tools', label: '工具调用' },
    { id: 'thinking', label: '思维链' },
    { id: 'reasoning', label: '推理' },
    { id: 'streaming', label: '流式输出' },
    { id: 'vision', label: '视觉识别' }
];

// 特性标签颜色映射
export const FEATURE_COLORS: Record<string, string> = {
  'structured_output': 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  'tool_call': 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  'thinking': 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  'agent_thought': 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
  'streaming': 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400',
  'image_input': 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400',
  'vision': 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400',
  'embedding': 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  'rerank': 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
};