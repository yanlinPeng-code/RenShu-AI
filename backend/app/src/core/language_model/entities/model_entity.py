#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/01 10:50
@Author  : thezehui@gmail.com
@File    : model_entity.py

模型实体定义，包含模型参数、特性、基础模型类等。
"""
from abc import ABC
from enum import Enum
from typing import Sequence, List, Dict

from langchain_core.language_models import BaseLanguageModel as LCBaseLanguageModel
from langchain_core.messages import HumanMessage, BaseMessage
from pydantic import BaseModel, Field
from typing_extensions import Any, Optional
import tiktoken


class DefaultModelParameterName(str, Enum):
    """默认的参数名字，一般是所有LLM都有的一些参数"""
    TEMPERATURE = "temperature"  # 温度
    TOP_P = "top_p"  # 核采样率
    PRESENCE_PENALTY = "presence_penalty"  # 存在惩罚
    FREQUENCY_PENALTY = "frequency_penalty"  # 频率惩罚
    MAX_TOKENS = "max_tokens"  # 要生成的内容的最大tokens数


class ModelType(str, Enum):
    """模型类型枚举"""
    CHAT = "chat"  # 聊天模型
    COMPLETION = "completion"  # 文本生成模型
    VISION="vision"


class ModelParameterType(str, Enum):
    """模型参数类型"""
    FLOAT = "float"
    INT = "int"
    STRING = "string"
    BOOLEAN = "boolean"


class ModelParameterOption(BaseModel):
    """模型参数选项配置模型"""
    label: str  # 配置选项标签
    value: Any  # 配置选项对应的值


class ModelParameter(BaseModel):
    """模型参数实体信息"""
    name: str = ""  # 参数名字
    label: str = ""  # 参数标签
    type: ModelParameterType = ModelParameterType.STRING  # 参数的类型
    help: str = ""  # 帮助信息
    required: bool = False  # 是否必填
    default: Optional[Any] = None  # 默认参数值
    min: Optional[float] = None  # 最小值
    max: Optional[float] = None  # 最大值
    precision: int = 2  # 保留小数的位数
    options: list[ModelParameterOption] = Field(default_factory=list)  # 可选的参数配置


class ModelFeature(str, Enum):
    """模型特性，用于标记模型支持的特性信息，涵盖工具调用、智能体推理、图片输入"""
    TOOL_CALL = "tool_call"  # 工具调用
    AGENT_THOUGHT = "agent_thought"  # 是否支持智能体推理，一般要求参数量比较大，能回答通用型任务，如果不支持推理则会直接生成答案，而不进行中间步骤
    IMAGE_INPUT = "image_input"  # 图片输入，多模态大语言模型
    CODE_INTERPRETER = "code_interpreter",
    WEB_SEARCH = "web_search"
    THINKING = "thinking",
    STRUCTURED_OUTPUT = "structured_output"
class ModelEntity(BaseModel):
    """语言模型实体，记录模型的相关信息"""
    model_name: str = Field(default="", alias="model")  # 模型名字，使用model作为别名
    label: str = ""  # 模型标签
    model_type: ModelType = ModelType.CHAT  # 模型类型
    features: list[ModelFeature] = Field(default_factory=list)  # 模型特征信息
    context_window: int = 0  # 上下文窗口长度(输入+输出的总长度)
    max_output_tokens: int = 0  # 最大输出内容长度(输出)
    attributes: dict[str, Any] = Field(default_factory=dict)  # 模型固定属性字典
    parameters: list[ModelParameter] = Field(default_factory=list)  # 模型参数字段规则列表，用于记录模型的配置参数
    metadata: dict[str, Any] = Field(default_factory=dict)  # 模型元数据，用于存储模型的额外数据，例如价格、词表等等信息


class BaseLanguageModel(LCBaseLanguageModel, ABC):
    """基础语言模型"""
    features: list[ModelFeature] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    model_id: str = ""  # 添加模型ID字段，用于统计
    tiktoken_model_name: str = "cl100k_base"  # 用于token计算的模型名称

    def get_pricing(self) -> tuple[float, float, float]:
        """获取模型价格信息"""
        input_price = self.metadata.get("pricing", {}).get("input", 0.0)
        output_price = self.metadata.get("pricing", {}).get("output", 0.0)
        unit = self.metadata.get("pricing", {}).get("unit", 0.0)

        return input_price, output_price, unit

    def convert_to_human_message(self, query: str, image_urls: list[str] = None):
        """将传递的query+image_url转换成人类消息HumanMessage，如果没有传递image_url或者该LLM不支持image_input，则直接返回普通人类消息"""
        # 1.判断图片url是否为空，或者该LLM不支持图片输入，则直接返回普通消息
        if image_urls is None or len(image_urls) == 0 or ModelFeature.IMAGE_INPUT not in self.features:
            return HumanMessage(content=query)

        # 2.存在图片输入并且支持多模态输入，则按照OpenAI规则转换成人类消息，如果模型有差异则直接继承重写
        #   链接: https://python.langchain.com/docs/how_to/multimodal_inputs/
        return HumanMessage(content=[
            {
                "type": "text",
                "text": query,
            },
            *[{"type": "image_url", "image_url": {"url": image_url}} for image_url in image_urls]

        ])




    
    # def get_tiktoken_encoding(self):
    #     """
    #     获取tiktoken编码器
    #
    #     Returns:
    #         tiktoken.Encoding: 编码器实例
    #     """
    #     try:
    #         return tiktoken.encoding_for_model(self.tiktoken_model_name)
    #     except KeyError:
    #         # 如果模型不被支持，使用默认的编码器
    #         return tiktoken.get_encoding("cl100k_base")
    #
    # def get_num_tokens_from_messages(self, messages) -> int:
    #     """
    #     使用tiktoken计算消息列表的token数量
    #
    #     Args:
    #         messages: 消息列表
    #
    #     Returns:
    #         int: token数量
    #     """
    #     try:
    #         encoding = self.get_tiktoken_encoding()
    #         tokens_per_message = 3
    #         tokens_per_name = 1
    #         num_tokens = 0
    #
    #         if isinstance(messages, list):
    #             for message in messages:
    #                 num_tokens += tokens_per_message
    #                 if isinstance(message, dict):
    #                     for key, value in message.items():
    #                         if value:
    #                             num_tokens += len(encoding.encode(str(value)))
    #                         if key == "name":
    #                             num_tokens += tokens_per_name
    #                 else:
    #                     # 假设是BaseMessage实例
    #                     num_tokens += len(encoding.encode(message.content))
    #         else:
    #             # 假设是单个消息
    #             num_tokens = len(encoding.encode(str(messages)))
    #
    #         num_tokens += 3  # 每条消息的额外token
    #         return num_tokens
    #     except Exception as e:
    #         print(f"使用tiktoken计算输入token时出错: {e}")
    #         # 出错时返回估算值
    #         return self._estimate_tokens_from_messages(messages)
    #
    # def get_num_tokens(self, text) -> int:
    #     """
    #     使用tiktoken计算文本的token数量
    #
    #     Args:
    #         text: 文本内容
    #
    #     Returns:
    #         int: token数量
    #     """
    #     try:
    #         encoding = self.get_tiktoken_encoding()
    #         return len(encoding.encode(str(text)))
    #     except Exception as e:
    #         print(f"使用tiktoken计算token时出错: {e}")
    #         # 出错时返回估算值
    #         return len(str(text)) // 4
    #
    # def _estimate_tokens_from_messages(self, messages) -> int:
    #     """
    #     估算消息列表的token数量
    #
    #     Args:
    #         messages: 消息列表
    #
    #     Returns:
    #         int: 估算的token数量
    #     """
    #     if isinstance(messages, list):
    #         text_content = "\n".join([
    #             msg.get("content", "") if isinstance(msg, dict)
    #             else str(msg) for msg in messages
    #         ])
    #         return len(text_content) // 4
    #     else:
    #         return len(str(messages)) // 4
    #
    # def invoke_with_stats(self, input, config=None, **kwargs):
    #     """
    #     调用模型并记录统计信息
    #
    #     Args:
    #         input: 输入内容
    #         config: 配置信息
    #         **kwargs: 其他参数
    #
    #     Returns:
    #         模型响应结果
    #     """
    #     # 调用模型
    #     response = super().invoke(input, config, **kwargs)
    #
    #     # 计算输入和输出token数量
    #     input_tokens = self.get_num_tokens_from_messages(input)
    #     output_tokens = self._calculate_output_tokens(response)
    #
    #     # 记录模型使用情况
    #     if self.model_id:
    #         model_manager.record_model_usage(
    #             self.model_id,
    #             input_tokens=input_tokens,
    #             output_tokens=output_tokens
    #         )
    #
    #     return response
    #
    # def _calculate_output_tokens(self, response) -> int:
    #     """
    #     计算输出token数量
    #
    #     Args:
    #         response: 模型响应
    #
    #     Returns:
    #         int: 输出token数量
    #     """
    #     try:
    #         # 如果响应有usage信息
    #         if hasattr(response, 'usage') and response.usage:
    #             return getattr(response.usage, 'completion_tokens', 0)
    #
    #         # 如果响应有额外的kwargs包含usage信息
    #         elif hasattr(response, 'additional_kwargs'):
    #             usage = response.additional_kwargs.get('usage')
    #             if usage and 'completion_tokens' in usage:
    #                 return usage['completion_tokens']
    #             elif usage and 'output_tokens' in usage:
    #                 return usage['output_tokens']
    #
    #             # 如果响应内容可以直接获取
    #         elif hasattr(response, 'content'):
    #             return self.get_num_tokens(response.content)
    #
    #             # 如果响应是字符串
    #         elif isinstance(response, str):
    #             return self.get_num_tokens(response)
    #
    #             # 如果响应是字典且包含content键
    #         elif isinstance(response, dict) and 'content' in response:
    #
    #         content = response['content']
    #             return self.get_num_tokens(content)
    #
    #         return 0
    #     except Exception as e:
    #         print(f"计算输出token时出错: {e}")
    #         return 0