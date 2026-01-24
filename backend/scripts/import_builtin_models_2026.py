import asyncio
import sys
import json
from pathlib import Path
from uuid import uuid4

# Add backend directory to path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from sqlalchemy import text
from app.src.common.config.prosgresql_config import async_db_manager

# ==================== DATA DEFINITIONS ====================

PROVIDERS = {
    # --- From User Images & Instructions (Preserved) ---
    "ollama": {
        "label": "Ollama",
        "description": "本地模型运行时（非云API）",
        "icon": None, 
        "default_base_url": "http://localhost:11434",
        "supported_model_types": ["llm", "multimodal", "embedding", "code"],
        "models": [
            {"model_name": "deepseek-v3.1:671b", "label": "DeepSeek V3.1", "context_window": 163840},
            {"model_name": "deepseek-v3.2", "label": "DeepSeek V3.2", "context_window": 163840},
            {"model_name": "gpt-oss:20b", "label": "GPT-OSS 20B", "context_window": 128000},
            {"model_name": "gpt-oss:120b", "label": "GPT-OSS 120B", "context_window": 128000},
            {"model_name": "qwen3-coder:480b", "label": "Qwen3 Coder 480B", "context_window": 262144, "model_type": "code"},
            {"model_name": "deepseek-r1", "label": "DeepSeek R1", "context_window": 64000},
            {"model_name": "deepseek-v3", "label": "DeepSeek V3 671B", "context_window": 64000},
            {"model_name": "llama3.1", "label": "Llama 3.1 8B", "context_window": 128000},
            {"model_name": "llama3.1:70b", "label": "Llama 3.1 70B", "context_window": 128000},
            {"model_name": "llama3.1:405b", "label": "Llama 3.1 405B", "context_window": 128000},
            {"model_name": "codellama", "label": "Code Llama 7B", "context_window": 16000, "model_type": "code"},
        ]
    },
    "vllm": {
        "label": "vLLM",
        "description": "High-throughput and memory-efficient LLM serving engine",
        "default_base_url": "http://localhost:8000/v1",
        "models": [
            {"model_name": "meta-llama/Meta-Llama-3.1-70B", "label": "Llama 3.1 70B", "context_window": 128000},
            {"model_name": "deepseek-ai/DeepSeek-V3", "label": "DeepSeek V3", "context_window": 64000},
            {"model_name": "Qwen/QwQ-32B-Preview", "label": "QwQ 32B Preview", "context_window": 32000},
            {"model_name": "Qwen/Qwen2-7B-Instruct", "label": "Qwen2 7B Instruct", "context_window": 32000},
            {"model_name": "meta-llama/Meta-Llama-3.1-405B-Instruct", "label": "Llama 3.1 405B Instruct", "context_window": 128000},
            {"model_name": "google/gemma-2-9b", "label": "Gemma 2 9B", "context_window": 8192},
            {"model_name": "google/gemma-2-27b", "label": "Gemma 2 27B", "context_window": 8192},
            {"model_name": "mistralai/Mistral-7B-Instruct-v0.1", "label": "Mistral 7B Instruct v0.1", "context_window": 8192},
            {"model_name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "label": "Mistral 8x7B Instruct v0.1", "context_window": 32000},
        ]
    },
    "xinference": {
        "label": "Xinference",
        "description": "Inference solution for LLMs, speech recognition, and multimodal models",
        "models": [
            {"model_name": "deepseek-v3", "label": "DeepSeek V3", "context_window": 163840},
            {"model_name": "deepseek-r1", "label": "DeepSeek R1", "context_window": 163840},
            {"model_name": "deepseek-r1-distill-llama", "label": "DeepSeek R1 Distill Llama", "context_window": 128000},
            {"model_name": "deepseek-r1-distill-qwen", "label": "DeepSeek R1 Distill Qwen", "context_window": 128000},
            {"model_name": "qwq-32b", "label": "QwQ 32B", "context_window": 32000},
            {"model_name": "qvq-72b-preview", "label": "QVQ 72B Preview", "context_window": 32000, "model_type": "multimodal"},
            {"model_name": "qwen2.5-instruct", "label": "Qwen2.5 Instruct", "context_window": 32000},
            {"model_name": "qwen2.5-coder-instruct", "label": "Qwen2.5 Coder Instruct", "context_window": 32000, "model_type": "code"},
            {"model_name": "qwen2.5-vl-instruct", "label": "Qwen2.5 VL Instruct", "context_window": 128000, "model_type": "multimodal"},
            {"model_name": "mistral-nemo-instruct", "label": "Mistral Nemo Instruct", "context_window": 1000000},
            {"model_name": "mistral-large-instruct", "label": "Mistral Large Instruct", "context_window": 128000},
        ]
    },
    
    # --- Merged Data from Markdown 2026-01-24 ---
    "openai": {
        "label": "OpenAI",
        "description": "全球领先的通用人工智能模型提供商",
        "default_base_url": "https://api.openai.com/v1",
        "help_url": "https://platform.openai.com/api-keys",
        "supported_model_types": ["llm", "multimodal", "embedding", "image", "audio", "code", "rerank"],
        "models": [
            {"model_name": "gpt-5", "label": "GPT-5", "model_type": "multimodal", "context_window": 256000, "features": ["reasoning", "thinking", "tool_call", "structured_output", "image_input", "image_generate", "speech2text", "tts", "streaming"], "default_max_tokens": 8192},
            {"model_name": "gpt-4o", "label": "GPT-4o", "model_type": "multimodal", "context_window": 128000, "features": ["reasoning", "tool_call", "structured_output", "image_input", "image_generate", "streaming"], "default_max_tokens": 4096},
            {"model_name": "gpt-4o-mini", "label": "GPT-4o Mini", "model_type": "multimodal", "context_window": 128000, "default_max_tokens": 4096},
            {"model_name": "text-embedding-3-large", "label": "Text Embedding 3 Large", "model_type": "embedding", "context_window": 8192, "features": ["dense", "batch"]},
            # Previous entries
            {"model_name": "gpt-5.2-instant", "label": "GPT-5.2 Instant", "context_window": 128000},
            {"model_name": "gpt-5.2-thinking", "label": "GPT-5.2 Thinking", "context_window": 200000, "features": ["thinking"]},
            {"model_name": "gpt-5.2-pro", "label": "GPT-5.2 Pro", "context_window": 1000000},
            {"model_name": "gpt-5.2-codex", "label": "GPT-5.2 Codex", "context_window": 128000, "model_type": "code"},
        ]
    },
    "anthropic": {
        "label": "Anthropic",
        "description": "专注安全与可控性的AI模型公司（Claude）",
        "default_base_url": "https://api.anthropic.com/v1",
        "help_url": "https://console.anthropic.com/settings/keys",
        "supported_model_types": ["llm", "multimodal"],
        "models": [
            {"model_name": "claude-opus-4.5", "label": "Claude Opus 4.5", "model_type": "multimodal", "context_window": 200000, "features": ["reasoning", "thinking", "tool_call", "structured_output", "image_input", "streaming"]},
            {"model_name": "claude-sonnet-4", "label": "Claude Sonnet 4", "model_type": "multimodal", "context_window": 200000, "features": ["reasoning", "tool_call", "structured_output"]},
            {"model_name": "claude-haiku-3.5", "label": "Claude Haiku 3.5", "model_type": "llm", "context_window": 200000, "features": ["streaming"]},
            # Previous entries
            {"model_name": "claude-opus-4", "label": "Claude 4 Opus", "context_window": 200000},
            {"model_name": "claude-sonnet-4.5", "label": "Claude 4.5 Sonnet", "context_window": 200000, "model_type": "code"},
        ]
    },
    "google": {
        "label": "Google AI",
        "description": "Google Gemini 系列模型",
        "default_base_url": "https://generativelanguage.googleapis.com/v1",
        "help_url": "https://ai.google.dev",
        "supported_model_types": ["llm", "multimodal", "embedding", "image", "video"],
        "models": [
            {"model_name": "gemini-3-pro", "label": "Gemini 3 Pro", "model_type": "multimodal", "context_window": 1000000, "features": ["reasoning", "thinking", "image_input", "image_generate", "video", "tool_call"]},
            {"model_name": "gemini-2.5-pro", "label": "Gemini 2.5 Pro", "model_type": "multimodal", "context_window": 1000000},
            {"model_name": "text-embedding-005", "label": "Text Embedding 005", "model_type": "embedding", "context_window": 8192},
            # Previous entries
            {"model_name": "gemini-3-flash", "label": "Gemini 3 Flash", "context_window": 1000000, "model_type": "multimodal"},
            {"model_name": "gemini-2.5-flash", "label": "Gemini 2.5 Flash", "context_window": 1000000, "model_type": "multimodal"},
        ]
    },
    "xai": {
        "label": "xAI",
        "description": "Elon Musk 创立的AI公司（Grok）",
        "default_base_url": "https://api.x.ai/v1",
        "help_url": "https://console.x.ai",
        "supported_model_types": ["llm", "multimodal"],
        "models": [
            {"model_name": "grok-beta", "label": "Grok Beta", "context_window": 128000},
        ]
    },
    "meta": {
        "label": "Meta AI",
        "description": "开源 Llama 系列模型",
        "supported_model_types": ["llm", "multimodal", "code"],
        "models": [
            {"model_name": "llama-3.3-405b", "label": "Llama 3.3 405B", "model_type": "llm", "context_window": 128000, "features": ["open_source", "reasoning"]},
        ]
    },
    "mistral": {
        "label": "Mistral AI",
        "default_base_url": "https://api.mistral.ai/v1",
        "supported_model_types": ["llm", "embedding", "code"],
        "models": [
            {"model_name": "mistral-large-2", "label": "Mistral Large 2", "model_type": "llm", "context_window": 128000, "features": ["reasoning", "tool_call"]},
            # Previous entries
            {"model_name": "mistral-3-large", "label": "Mistral 3 Large", "context_window": 128000},
            {"model_name": "mistral-3-medium", "label": "Mistral 3 Medium", "context_window": 32000},
        ]
    },
    "cohere": {
        "label": "Cohere",
        "default_base_url": "https://api.cohere.ai/v1",
        "supported_model_types": ["llm", "embedding", "rerank"],
        "models": [
            {"model_name": "command-r-plus", "label": "Command R+", "model_type": "llm", "context_window": 128000, "features": ["tool_call", "rerank"]},
        ]
    },
    "deepseek": {
        "label": "DeepSeek",
        "description": "中国高性能推理与代码模型厂商",
        "default_base_url": "https://api.deepseek.com/v1",
        "supported_model_types": ["llm", "code", "multimodal"],
        "models": [
            {"model_name": "deepseek-v3.2", "label": "DeepSeek V3.2", "model_type": "llm", "context_window": 128000, "features": ["reasoning", "tool_call", "structured_output"]},
            {"model_name": "deepseek-r1", "label": "DeepSeek R1", "model_type": "llm", "context_window": 128000, "features": ["reasoning", "thinking"]},
            # Previous
            {"model_name": "deepseek-v3", "label": "DeepSeek V3", "context_window": 64000},
        ]
    },
    "alibaba": {
        "label": "Alibaba Cloud (Qwen)",
        "default_base_url": "https://dashscope.aliyuncs.com/api/v1",
        "supported_model_types": ["llm", "multimodal", "code", "image", "audio", "video", "embedding"],
        "models": [
            {"model_name": "qwen3-max", "label": "Qwen3 Max", "model_type": "multimodal", "context_window": 1000000, "features": ["reasoning", "thinking", "tool_call", "image_input"]},
            {"model_name": "qwen3-vl-235b", "label": "Qwen3 VL 235B", "model_type": "multimodal", "context_window": 1000000, "features": ["image_input", "reasoning", "tool_call"]},
            {"model_name": "qwen3-coder-plus", "label": "Qwen3 Coder Plus", "model_type": "code", "context_window": 256000, "features": ["code_generation", "tool_call"]},
        ]
    },
    # Keep bailian for compatibility or map to alibaba? Keeping separate if key differs, but logic suggests merge. 
    # For now, we'll keep both if user used "bailian" previously, but "alibaba" is the new key in doc.
    "bailian": {
        "label": "Alibaba Bailian (Legacy)",
        "models": [
            {"model_name": "qwen-3-max", "label": "Qwen 3 Max", "context_window": 32768},
            {"model_name": "qwen-2.5-max", "label": "Qwen 2.5 Max", "context_window": 32768},
        ]
    },
    "moonshot": {
        "label": "Moonshot AI",
        "default_base_url": "https://api.moonshot.cn/v1",
        "supported_model_types": ["llm", "multimodal"],
        "models": [
            {"model_name": "kimi-k2", "label": "Kimi K2", "model_type": "llm", "context_window": 2000000, "features": ["long_context", "reasoning"]},
            # Previous
            {"model_name": "kimi-k2-thinking", "label": "Kimi K2 Thinking", "context_window": 262144, "features": ["thinking"]},
            {"model_name": "kimi-k2-0905-preview", "label": "Kimi K2 0905", "context_window": 262144},
            {"model_name": "kimi-latest", "label": "Kimi Latest", "context_window": 128000},
            {"model_name": "moonshot-v1-auto", "label": "Moonshot V1 Auto", "context_window": 128000},
        ]
    },
    "zhipu": {
        "label": "Zhipu AI",
        "default_base_url": "https://open.bigmodel.cn/api/paas/v4",
        "supported_model_types": ["llm", "multimodal", "code", "embedding"],
        "models": [
            {"model_name": "glm-4.6", "label": "GLM-4.6", "model_type": "multimodal", "context_window": 128000, "features": ["reasoning", "image_input", "tool_call"]},
            {"model_name": "glm-4", "label": "GLM-4", "context_window": 128000},
        ]
    },
    "baichuan": {
        "label": "Baichuan AI",
        "supported_model_types": ["llm"],
        "models": [] # No specific models in doc, placeholder
    },
    "baidu": {
        "label": "Baidu ERNIE",
        "default_base_url": "https://aip.baidubce.com",
        "supported_model_types": ["llm", "multimodal", "embedding"],
        "models": []
    },
    "iflytek": {
        "label": "iFlytek",
        "supported_model_types": ["llm", "multimodal", "audio"],
        "models": []
    },
    "bytedance": {
        "label": "ByteDance",
        "description": "Doubao Models",
        "models": [
            {"model_name": "doubao-1.8-pro", "label": "Doubao 1.8 Pro", "context_window": 128000},
            {"model_name": "seed-1.8", "label": "Seed 1.8", "context_window": 128000},
        ]
    },
    "minimax": {
        "label": "MiniMax",
        "models": [
            {"model_name": "abab6.5-chat", "label": "Abab 6.5", "context_window": 32000},
        ]
    },
    "openrouter": {
        "label": "OpenRouter",
        "description": "Unified interface for LLMs",
        "default_base_url": "https://openrouter.ai/api/v1",
        "models": []
    }
}

async def import_models():
    print("Starting 2026 Model Import...")
    await async_db_manager.init()
    
    async with async_db_manager.async_engine.begin() as conn:
        try:
            position_counter = 0
            
            for provider_key, provider_data in PROVIDERS.items():
                position_counter += 1
                name = provider_key
                
                # 1. Insert/Update Provider
                print(f"Processing Provider: {provider_data['label']} ({name})")
                
                # Check if exists (case-insensitive)
                res = await conn.execute(text("SELECT id FROM system_model_providers WHERE lower(name) = lower(:name)"), {"name": name})
                provider_id = res.scalar()
                
                if not provider_id:
                    provider_id = uuid4()
                    await conn.execute(text("""
                        INSERT INTO system_model_providers 
                        (id, name, label, description, default_base_url, supported_model_types, help_url, position, created_at, updated_at)
                        VALUES (:id, :name, :label, :description, :default_base_url, :supported_model_types, :help_url, :position, now(), now())
                    """), {
                        "id": provider_id,
                        "name": name,
                        "label": provider_data["label"],
                        "description": provider_data.get("description"),
                        "default_base_url": provider_data.get("default_base_url"),
                        "supported_model_types": json.dumps(provider_data.get("supported_model_types", ["llm"])),
                        "help_url": provider_data.get("help_url"),
                        "position": position_counter
                    })
                else:
                    # Update existing provider
                    await conn.execute(text("""
                        UPDATE system_model_providers 
                        SET label = :label, 
                            description = :description, 
                            default_base_url = :default_base_url,
                            supported_model_types = :supported_model_types,
                            help_url = :help_url
                        WHERE id = :id
                    """), {
                        "id": provider_id,
                        "label": provider_data["label"],
                        "description": provider_data.get("description"),
                        "default_base_url": provider_data.get("default_base_url"),
                        "supported_model_types": json.dumps(provider_data.get("supported_model_types", ["llm"])),
                        "help_url": provider_data.get("help_url")
                    })
                
                # 2. Insert/Update Models
                model_pos = 0
                for model_data in provider_data["models"]:
                    model_pos += 1
                    model_name = model_data["model_name"]
                    
                    # Check if exists
                    res = await conn.execute(text("""
                        SELECT id FROM system_model_definitions 
                        WHERE provider_id = :pid AND model_name = :mname
                    """), {"pid": provider_id, "mname": model_name})
                    model_id = res.scalar()
                    
                    params = {
                        "provider_id": provider_id,
                        "model_name": model_name,
                        "label": model_data["label"],
                        "model_type": model_data.get("model_type", "llm"),
                        "context_window": model_data.get("context_window", 4096),
                        "default_max_tokens": model_data.get("default_max_tokens", 4096),
                        "features": json.dumps(model_data.get("features", [])),
                        "default_parameters": json.dumps({}),
                        "position": model_pos,
                        "is_enabled": True
                    }
                    
                    if not model_id:
                        params["id"] = uuid4()
                        await conn.execute(text("""
                            INSERT INTO system_model_definitions
                            (id, provider_id, model_name, label, model_type, context_window, default_max_tokens, features, default_parameters, position, is_enabled, created_at, updated_at)
                            VALUES (:id, :provider_id, :model_name, :label, :model_type, :context_window, :default_max_tokens, :features, :default_parameters, :position, :is_enabled, now(), now())
                        """), params)
                        print(f"  + Added Model: {model_name}")
                    else:
                        params["id"] = model_id
                        await conn.execute(text("""
                            UPDATE system_model_definitions
                            SET label = :label,
                                context_window = :context_window,
                                default_max_tokens = :default_max_tokens,
                                features = :features
                            WHERE id = :id
                        """), params)
                        print(f"  . Updated Model: {model_name}")

            print("Import completed successfully.")
            
        except Exception as e:
            print(f"Error during import: {e}")
            raise

    await async_db_manager.close()

if __name__ == "__main__":
    asyncio.run(import_models())
