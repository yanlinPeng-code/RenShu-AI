import providerAnthropic from '../assets/provider/provider.anthropic.svg';
import providerBailian from '../assets/provider/provider.bailian.svg';
import providerBytedance from '../assets/provider/provider.bytedance.svg';
import providerMinimax from '../assets/provider/provider.minimax.svg';
import providerMoonshot from '../assets/provider/provider.moonshot.svg';
import providerOllama from '../assets/provider/provider.ollama.svg';
import providerOpenai from '../assets/provider/provider.openai.svg';
import providerOpenrouter from '../assets/provider/provider.openrouter.svg';
import providerX from '../assets/provider/provider.x.svg';
import providerXinference from '../assets/provider/provider.xinference.svg';
import providerZhipu from '../assets/provider/provider.zhipu.svg';
import providerGoogle from '../assets/provider/provider.google.svg';
import providerVllm from '../assets/provider/provider.vllm.svg';
import providerDeepseek from '../assets/provider/provider.deepseek.svg';
import providerBaichuan from '../assets/provider/provider.baichuan.svg';
import providerWenxin from '../assets/provider/provider.wenxin.svg';



import modelChatglm from '../assets/model/model.chatglm.svg';
import modelClaude from '../assets/model/model.claude.svg';
import modelDeepseek from '../assets/model/model.deepseek.svg';
import modelDoubao from '../assets/model/model.doubao.svg';
import modelGemini from '../assets/model/model.gemini.svg';
import modelGrok from '../assets/model/model.grok.svg';
import modelKimi from '../assets/model/model.kimi.svg';
import modelMinimax from '../assets/model/model.minimax.svg';
import modelQwen from '../assets/model/model.qwen.svg';
import modelMeta from '../assets/model/model.meta.svg';
import modelGpt from '../assets/model/model.gpt.svg';


export const getProviderIconPath = (name: string): string | undefined => {
  if (!name) return undefined;
  const lowerName = name.toLowerCase();

  if (lowerName === 'openai' || lowerName.includes('openai')) return providerOpenai;
  if (lowerName === 'ollama' || lowerName.includes('ollama')) return providerOllama;
  if (lowerName === 'google' || lowerName.includes('google')) return providerGoogle;
  if (lowerName === 'vllm' || lowerName.includes('vllm')) return providerVllm;
  if (lowerName === 'deepseek' || lowerName.includes('deepseek')) return providerDeepseek;
  if (lowerName.includes('anthropic') || lowerName==='anthropic') return providerAnthropic;
  if (lowerName.includes('bailian') || lowerName.includes('alibaba') || lowerName==='bailian' || lowerName==='alibaba') return providerBailian;
  if (lowerName.includes('bytedance')|| lowerName==='bytedance') return providerBytedance;
  if (lowerName.includes('minimax')|| lowerName==='minimax') return providerMinimax;
  if (lowerName.includes('moonshot') || lowerName==='moonshot') return providerMoonshot;
  if (lowerName.includes('openrouter') || lowerName==='openrouter') return providerOpenrouter;
  if (lowerName.includes('xinference') || lowerName==='xinference') return providerXinference;
  if (lowerName === 'x' || lowerName === 'xai') return providerX;
  if (lowerName.includes('zhipu') || lowerName==='zhipu') return providerZhipu;
  if (lowerName.includes('baichuan') || lowerName==='baichuan') return providerBaichuan;
  if (lowerName.includes('wenxin') || lowerName==='wenxin') return providerWenxin;



  return undefined;
};

export const getModelIconPath = (name: string): string | undefined => {
  if (!name) return undefined;
  const lowerName = name.toLowerCase();

  if (lowerName.includes('glm') || lowerName.includes('chatglm')) return modelChatglm;
  if (lowerName.includes('gpt') || lowerName.includes('openai')) return modelGpt;
  if (lowerName.includes('claude')) return modelClaude;
  if (lowerName.includes('deepseek')) return modelDeepseek;
  if (lowerName.includes('gemini')) return modelGemini;
  if (lowerName.includes('doubao')) return modelDoubao;
  if (lowerName.includes('grok')) return modelGrok;
  if (lowerName.includes('kimi')) return modelKimi;
  if (lowerName.includes('minimax')) return modelMinimax;
  if (lowerName.includes('qwen') || lowerName.includes('qwq') || lowerName.includes('qvq')) return modelQwen;
  if (lowerName.includes('meta') || lowerName.includes('llama')) return modelMeta;
  
  return undefined;
};
