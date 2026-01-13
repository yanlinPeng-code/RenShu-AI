from dataclasses import dataclass, field
from typing import Dict, Optional
from threading import Lock
from datetime import datetime, timedelta


@dataclass
class ModelStats:
    """模型使用统计信息"""
    call_count: int = 0  # 调用次数
    total_input_tokens: int = 0  # 总输入token数
    total_output_tokens: int = 0  # 总输出token数
    last_used: Optional[datetime] = None  # 最后使用时间


class ModelStatsManager:
    """模型统计管理器"""
    
    def __init__(self):
        self._stats: Dict[str, ModelStats] = {}
        self._lock = Lock()
    
    def record_call(self, model_id: str, input_tokens: int = 0, output_tokens: int = 0):
        """记录模型调用"""
        with self._lock:
            if model_id not in self._stats:
                self._stats[model_id] = ModelStats()
            
            stats = self._stats[model_id]
            stats.call_count += 1
            stats.total_input_tokens += input_tokens
            stats.total_output_tokens += output_tokens
            stats.last_used = datetime.now()
    
    def get_stats(self, model_id: str) -> Optional[ModelStats]:
        """获取指定模型的统计信息"""
        return self._stats.get(model_id)
    
    def get_all_stats(self) -> Dict[str, ModelStats]:
        """获取所有模型的统计信息"""
        return self._stats.copy()
    
    def reset_stats(self, model_id: str = None):
        """重置统计信息"""
        with self._lock:
            if model_id:
                if model_id in self._stats:
                    self._stats[model_id] = ModelStats()
            else:
                self._stats.clear()
    
    def get_recent_stats(self, hours: int = 24) -> Dict[str, ModelStats]:
        """获取最近一段时间内的统计信息"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_stats = {}
        
        with self._lock:
            for model_id, stats in self._stats.items():
                if stats.last_used and stats.last_used >= cutoff_time:
                    recent_stats[model_id] = stats
        
        return recent_stats


# 全局模型统计管理器实例
model_stats_manager = ModelStatsManager()