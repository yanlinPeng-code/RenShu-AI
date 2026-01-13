"""
数据模型Schema模块

提供所有数据模型Schema的统一导入接口。
"""

# 用户相关Schema
from .user_schema import (
    UserCreate, UserUpdate, PatientCreate, PatientUpdate,
    UserSessionCreate, UserSessionUpdate, UserStateCreate, UserStateUpdate,
    UserActivityCreate, UserActivityUpdate, AuthResponse, DeviceType, ActivityType,
    UserLogin
)

# 医疗相关Schema
from .medical_schema import (
    MedicalCaseCreate, MedicalCaseUpdate
)

# 药材相关Schema
from .herb_schema import (
    HerbCreate, HerbUpdate, HerbInventoryCreate, HerbInventoryUpdate,
    PrescriptionCreate, PrescriptionUpdate
)

# 对话相关Schema
from .conversation_schema import (
    ConversationCreate, ConversationUpdate, MessageCreate, MessageUpdate,
    ConversationSummary
)

# 系统相关Schema
from .system_schema import (
    SystemConfigCreate, SystemConfigUpdate
)

__all__ = [
    # 用户相关
    "UserCreate", "UserUpdate", "PatientCreate", "PatientUpdate",
    "UserSessionCreate", "UserSessionUpdate", "UserStateCreate", "UserStateUpdate",
    "UserActivityCreate", "UserActivityUpdate", "AuthResponse", "DeviceType", "ActivityType",
    "UserLogin",
    
    # 医疗相关
    "MedicalCaseCreate", "MedicalCaseUpdate",
    
    # 药材相关
    "HerbCreate", "HerbUpdate", "HerbInventoryCreate", "HerbInventoryUpdate",
    "PrescriptionCreate", "PrescriptionUpdate",
    # 对话相关
    "ConversationCreate", "ConversationUpdate", "MessageCreate", "MessageUpdate",
    "ConversationSummary",
    
    # 系统相关
    "SystemConfigCreate", "SystemConfigUpdate",
]