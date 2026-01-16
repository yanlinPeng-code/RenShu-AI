"""
医疗数据模型

定义医疗相关的数据结构和验证规则。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Index,Column,JSON
from pydantic import field_validator, ConfigDict


class MedicalCase(SQLModel, table=True):
    """病例模型"""
    __tablename__ = "medical_cases"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="病例ID")
    patient_id: UUID = Field(foreign_key="patients.id", description="患者ID")
    case_code: str = Field(max_length=20, unique=True, description="病例编号")
    chief_complaint: str = Field(description="主诉")
    present_illness: Optional[str] = Field(default=None, description="现病史")
    symptoms: Dict[str, str] = Field(sa_column=Column(JSON,nullable=True),description="症状描述（JSON格式存储）")
    tongue_description: Optional[str] = Field(default=None, description="舌象描述")
    pulse_description: Optional[str] = Field(default=None, description="脉象描述")
    syndrome_type: Optional[str] = Field(default=None, max_length=100, description="辨证结果（证型）")
    syndrome_confidence: Optional[Decimal] = Field(default=None, description="辨证置信度（0-1）")
    treatment_principle: Optional[str] = Field(default=None, description="治则治法")
    prescription_name: Optional[str] = Field(default=None, max_length=100, description="推荐方剂名称")
    prescription_ingredients: Dict[str, str] = Field(sa_column=Column(JSON,nullable=True), description="方剂组成（JSON格式）")
    dosage_instruction: Optional[str] = Field(default=None, description="用法用量")
    precautions: Optional[str] = Field(default=None, description="注意事项")
    follow_up_date: Optional[date] = Field(default=None, description="复诊日期")
    status: str = Field(default="active", description="病例状态")
    doctor_notes: Optional[str] = Field(default=None, description="医生备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_medical_cases_patient_id", "patient_id"),
        Index("idx_medical_cases_case_code", "case_code"),
        Index("idx_medical_cases_syndrome_type", "syndrome_type"),
        Index("idx_medical_cases_status", "status"),
        Index("idx_medical_cases_created_at", "created_at"),
        {"extend_existing": True}
    )
    
    @field_validator('status')
    def validate_status(cls, v):
        """验证病例状态"""
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
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )


class Symptom(SQLModel, table=True):
    """症状模型"""
    __tablename__ = "symptoms"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="症状ID")
    name: str = Field(max_length=100, description="症状名称")
    category: str = Field(max_length=50, description="症状分类（如：寒热、汗出、二便等）")
    description: Optional[str] = Field(default=None, description="症状描述")
    severity_levels: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable=True), description="严重程度分级（JSON格式）")
    related_syndromes: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable=True), description="相关证型（JSON格式）")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_symptoms_name", "name"),
        Index("idx_symptoms_category", "category"),
        Index("idx_symptoms_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class Syndrome(SQLModel, table=True):
    """证型模型"""
    __tablename__ = "syndromes"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="证型ID")
    name: str = Field(max_length=100, description="证型名称")
    category: str = Field(max_length=50, description="证型分类（如：八纲辨证、脏腑辨证等）")
    description: Optional[str] = Field(default=None, description="证型描述")
    main_symptoms: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable=True,default={}), description="主要症状（JSON格式）")
    treatment_principle: Optional[str] = Field(default=None, description="治则治法")
    common_prescriptions: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable=True,default={}), description="常用方剂（JSON格式）")
    precautions: Optional[str] = Field(default=None, description="注意事项")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_syndromes_name", "name"),
        Index("idx_syndromes_category", "category"),
        Index("idx_syndromes_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class MedicalRecord(SQLModel, table=True):
    """医案模型"""
    __tablename__ = "medical_records"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="医案ID")
    case_title: str = Field(max_length=200, description="医案标题")
    patient_age: Optional[int] = Field(default=None, description="患者年龄")
    patient_gender: Optional[str] = Field(default=None, max_length=10, description="患者性别")
    chief_complaint: str = Field(description="主诉")
    present_illness: str = Field(description="现病史")
    symptoms: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable=True,default={}),description="症状（JSON格式）")
    tongue_pulse: Optional[str] = Field(default=None, description="舌脉")
    syndrome_diagnosis: str = Field(max_length=100, description="证型诊断")
    treatment_principle: Optional[str] = Field(default=None, description="治则治法")
    prescription: str = Field(description="方药")
    dosage_instruction: Optional[str] = Field(default=None, description="用法用量")
    treatment_course: Optional[str] = Field(default=None, description="治疗经过")
    outcome: Optional[str] = Field(default=None, description="治疗结果")
    doctor_name: Optional[str] = Field(default=None, max_length=50, description="医生姓名")
    hospital_name: Optional[str] = Field(default=None, max_length=100, description="医院名称")
    case_source: Optional[str] = Field(default=None, max_length=100, description="医案来源")
    tags: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable=True,default={}), description="标签（JSON格式）")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_medical_records_syndrome_diagnosis", "syndrome_diagnosis"),
        Index("idx_medical_records_doctor_name", "doctor_name"),
        Index("idx_medical_records_hospital_name", "hospital_name"),
        Index("idx_medical_records_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    @field_validator('patient_gender')
    def validate_gender(cls, v):
        """验证性别"""
        if v is not None:
            allowed_genders = ['male', 'female', 'other']
            if v not in allowed_genders:
                raise ValueError(f'性别必须是以下之一: {", ".join(allowed_genders)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class TongueAnalysis(SQLModel, table=True):
    """舌苔分析模型"""
    __tablename__ = "tongue_analysis"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="分析ID")
    user_id: Optional[UUID] = Field(foreign_key="users.id", description="用户ID")
    image_url: str = Field(max_length=255, description="舌苔图片URL")
    analysis_result: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON,nullable= True,default={}), description="分析结果（JSON格式）")
    color_analysis: Optional[str] = Field(default=None, max_length=100, description="颜色分析")
    coating_thickness: Optional[str] = Field(default=None, max_length=50, description="苔质厚薄")
    coating_moisture: Optional[str] = Field(default=None, max_length=50, description="苔质润燥")
    coating_color: Optional[str] = Field(default=None, max_length=50, description="苔色")
    tongue_shape: Optional[str] = Field(default=None, max_length=50, description="舌形")
    syndrome_suggestion: Optional[str] = Field(default=None, description="证型建议")
    confidence_score: Optional[Decimal] = Field(default=None, description="置信度")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_tongue_analysis_user_id", "user_id"),
        Index("idx_tongue_analysis_created_at", "created_at"),
        {"extend_existing": True}
    )
    
    @field_validator('confidence_score')
    def validate_confidence(cls, v):
        """验证置信度"""
        if v is not None and (v < 0 or v > 1):
            raise ValueError('置信度必须在0-1之间')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )


class PrescriptionRecommendation(SQLModel, table=True):
    """方剂推荐模型"""
    __tablename__ = "prescription_recommendations"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="推荐ID")
    case_id: Optional[UUID] = Field(default_factory=uuid4, foreign_key="medical_cases.id", description="关联病例ID")
    user_id: Optional[UUID] = Field(foreign_key="users.id", description="用户ID")
    prescription_id: Optional[UUID] = Field(default_factory=uuid4, foreign_key="prescriptions.id", description="推荐方剂ID")
    prescription_name: str = Field(max_length=100, description="方剂名称")
    syndrome_type: Optional[str] = Field(default=None, max_length=100, description="对应证型")
    recommendation_reason: Optional[str] = Field(default=None, description="推荐理由")
    dosage_instruction: Optional[str] = Field(default=None, description="用法用量")
    precautions: Optional[str] = Field(default=None, description="注意事项")
    confidence_score: Optional[Decimal] = Field(default=None, description="推荐置信度")
    status: str = Field(default="recommended", description="推荐状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_prescription_recommendations_case_id", "case_id"),
        Index("idx_prescription_recommendations_user_id", "user_id"),
        Index("idx_prescription_recommendations_prescription_id", "prescription_id"),
        Index("idx_prescription_recommendations_status", "status"),
        Index("idx_prescription_recommendations_created_at", "created_at"),
        {"extend_existing": True}
    )
    
    @field_validator('status')
    def validate_status(cls, v):
        """验证推荐状态"""
        allowed_statuses = ['recommended', 'accepted', 'rejected', 'modified']
        if v not in allowed_statuses:
            raise ValueError(f'推荐状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v
    
    @field_validator('confidence_score')
    def validate_confidence(cls, v):
        """验证置信度"""
        if v is not None and (v < 0 or v > 1):
            raise ValueError('置信度必须在0-1之间')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )