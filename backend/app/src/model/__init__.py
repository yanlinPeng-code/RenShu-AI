"""
数据模型模块

提供所有数据模型的统一导入接口。
"""

# 用户相关模型 (基础模型，其他模型可能依赖它)
# from .user_model import (
#     User, Patient as OldPatient, UserSession, UserState, UserActivity, DeviceType, ActivityType, RefreshToken
# )

# 账户相关模型 (新的三端分离设计)
from .account_model import (
    Account, Patient, Doctor, Admin, AccountType, AccountRefreshToken, AccountActivity,UserState
)

# 对话相关模型
from .conversation_models import (
    Conversation, Message
)

# 医疗相关模型
from .medical_models import (
    MedicalCase, Symptom, Syndrome, MedicalRecord, TongueAnalysis,
    PrescriptionRecommendation
)

# 药材相关模型
from .herb_models import (
    Herb, HerbInventory, Prescription, ClassicText
)

# 系统相关模型
from .system_models import (
    SystemConfig, SystemStats, DatabaseStats, HealthCheck, LogEntry,
    AuditLog, BackupInfo, SystemInfo
)
from .model_config_models import (UserProviderConfig)

__all__ = [
    # 用户相关
    # "User", "UserSession",  "UserActivity", "DeviceType", "ActivityType", "RefreshToken",
     "UserProviderConfig",
    # 账户相关 (新的三端分离设计)
    "Account", "Patient", "Doctor", "Admin", "AccountType", "AccountRefreshToken", "AccountActivity","UserState",

    # 对话相关
    "Conversation", "Message",

    # 医疗相关
    "MedicalCase", "Symptom", "Syndrome", "MedicalRecord", "TongueAnalysis",
    "PrescriptionRecommendation",

    # 药材相关
    "Herb", "HerbInventory", "Prescription", "ClassicText",

    # 系统相关
    "SystemConfig", "SystemStats", "DatabaseStats", "HealthCheck", "LogEntry",
    "AuditLog", "BackupInfo", "SystemInfo"
]
