from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict



# 创建和更新模型
class MedicalCaseCreate(BaseModel):
    """病例创建模型"""

    patient_id: int = Field(description="患者ID")
    case_code: str = Field(description="病例编号")
    chief_complaint: str = Field(description="主诉")
    present_illness: Optional[str] = Field(default=None, description="现病史")
    symptoms: str = Field(description="症状描述（JSON格式存储）")
    tongue_description: Optional[str] = Field(default=None, description="舌象描述")
    pulse_description: Optional[str] = Field(default=None, description="脉象描述")
    syndrome_type: Optional[str] = Field(default=None, description="辨证结果（证型）")
    syndrome_confidence: Optional[Decimal] = Field(default=None, description="辨证置信度（0-1）")
    treatment_principle: Optional[str] = Field(default=None, description="治则治法")
    prescription_name: Optional[str] = Field(default=None, description="推荐方剂名称")
    prescription_ingredients: Optional[str] = Field(default=None, description="方剂组成（JSON格式）")
    dosage_instruction: Optional[str] = Field(default=None, description="用法用量")
    precautions: Optional[str] = Field(default=None, description="注意事项")
    follow_up_date: Optional[date] = Field(default=None, description="复诊日期")
    doctor_notes: Optional[str] = Field(default=None, description="医生备注")

    @field_validator('syndrome_confidence')
    def validate_confidence(cls, v):
        """验证置信度"""
        if v is not None and (v < 0 or v > 1):
            raise ValueError('置信度必须在0-1之间')
        return v

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )


class MedicalCaseUpdate(BaseModel):
    """病例更新模型"""

    chief_complaint: Optional[str] = Field(default=None, description="主诉")
    present_illness: Optional[str] = Field(default=None, description="现病史")
    symptoms: Optional[str] = Field(default=None, description="症状描述（JSON格式存储）")
    tongue_description: Optional[str] = Field(default=None, description="舌象描述")
    pulse_description: Optional[str] = Field(default=None, description="脉象描述")
    syndrome_type: Optional[str] = Field(default=None, description="辨证结果（证型）")
    syndrome_confidence: Optional[Decimal] = Field(default=None, description="辨证置信度（0-1）")
    treatment_principle: Optional[str] = Field(default=None, description="治则治法")
    prescription_name: Optional[str] = Field(default=None, description="推荐方剂名称")
    prescription_ingredients: Optional[str] = Field(default=None, description="方剂组成（JSON格式）")
    dosage_instruction: Optional[str] = Field(default=None, description="用法用量")
    precautions: Optional[str] = Field(default=None, description="注意事项")
    follow_up_date: Optional[date] = Field(default=None, description="复诊日期")
    status: Optional[str] = Field(default=None, description="病例状态")
    doctor_notes: Optional[str] = Field(default=None, description="医生备注")

    @field_validator('status')
    def validate_status(cls, v):
        """验证病例状态"""
        if v is not None:
            allowed_statuses = ['active', 'completed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f'病例状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @field_validator('syndrome_confidence')
    def validate_confidence(cls, v):
        """验证置信度"""
        if v is not None and (v < 0 or v > 1):
            raise ValueError('置信度必须在0-1之间')
        return v

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )