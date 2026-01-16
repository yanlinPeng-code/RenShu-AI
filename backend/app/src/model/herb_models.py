"""
药材数据模型

定义药材相关的数据结构和验证规则。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field, Relationship, Index
from pydantic import field_validator, ConfigDict


class Herb(SQLModel, table=True):
    """药材模型"""
    __tablename__ = "herbs"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="药材ID")
    name: str = Field(max_length=100, description="药材名称")
    pinyin: Optional[str] = Field(default=None, max_length=100, description="拼音")
    latin_name: Optional[str] = Field(default=None, max_length=100, description="拉丁学名")
    category: Optional[str] = Field(default=None, max_length=50, description="药材分类（如：补虚药、清热药等）")
    nature: Optional[str] = Field(default=None, max_length=20, description="药性（寒、热、温、凉、平）")
    flavor: Optional[str] = Field(default=None, max_length=50, description="五味（辛、甘、酸、苦、咸）")
    meridian: Optional[str] = Field(default=None, max_length=100, description="归经")
    effect: Optional[str] = Field(default=None, description="功效")
    indication: Optional[str] = Field(default=None, description="主治")
    usage_dosage: Optional[str] = Field(default=None, description="用法用量")
    contraindications: Optional[str] = Field(default=None, description="禁忌")
    incompatibilities: Optional[str] = Field(default=None, description="配伍禁忌（十八反、十九畏等）")
    processing_method: Optional[str] = Field(default=None, description="炮制方法")
    storage_method: Optional[str] = Field(default=None, description="贮藏方法")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_herbs_name", "name"),
        Index("idx_herbs_category", "category"),
        Index("idx_herbs_nature", "nature"),
        Index("idx_herbs_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    @field_validator('nature')
    def validate_nature(cls, v):
        """验证药性"""
        if v is not None:
            allowed_natures = ['寒', '热', '温', '凉', '平']
            if v not in allowed_natures:
                raise ValueError(f'药性必须是以下之一: {", ".join(allowed_natures)}')
        return v
    
    @field_validator('flavor')
    def validate_flavor(cls, v):
        """验证五味"""
        if v is not None:
            allowed_flavors = ['辛', '甘', '酸', '苦', '咸']
            if v not in allowed_flavors:
                raise ValueError(f'五味必须是以下之一: {", ".join(allowed_flavors)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class HerbInventory(SQLModel, table=True):
    """药材库存模型"""
    __tablename__ = "herb_inventory"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="库存ID")
    herb_id: UUID = Field(foreign_key="herbs.id", description="药材ID")
    batch_number: Optional[str] = Field(default=None, max_length=50, description="批次号")
    supplier: Optional[str] = Field(default=None, max_length=100, description="供应商")
    purchase_date: Optional[date] = Field(default=None, description="采购日期")
    expiry_date: Optional[date] = Field(default=None, description="过期日期")
    quantity: Decimal = Field(description="库存数量")
    unit: str = Field(max_length=20, description="单位（克、千克等）")
    unit_price: Optional[Decimal] = Field(default=None, description="单价")
    quality_grade: Optional[str] = Field(default=None, max_length=20, description="质量等级")
    storage_location: Optional[str] = Field(default=None, max_length=100, description="存储位置")
    status: str = Field(default="available", description="库存状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_herb_inventory_herb_id", "herb_id"),
        Index("idx_herb_inventory_batch_number", "batch_number"),
        Index("idx_herb_inventory_status", "status"),
        Index("idx_herb_inventory_expiry_date", "expiry_date"),
        {"extend_existing": True}
    )
    
    @field_validator('status')
    def validate_status(cls, v):
        """验证库存状态"""
        allowed_statuses = ['available', 'low_stock', 'out_of_stock', 'expired']
        if v not in allowed_statuses:
            raise ValueError(f'库存状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v
    
    @field_validator('quantity')
    def validate_quantity(cls, v):
        """验证数量"""
        if v < 0:
            raise ValueError('库存数量不能为负数')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )


class Prescription(SQLModel, table=True):
    """方剂模型"""
    __tablename__ = "prescriptions"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="方剂ID")
    name: str = Field(max_length=100, description="方剂名称")
    source: Optional[str] = Field(default=None, max_length=100, description="出处（如：《伤寒论》、《金匮要略》等）")
    category: Optional[str] = Field(default=None, max_length=50, description="方剂分类")
    composition: Optional[Dict[str, str] ]= Field(sa_column=Column(JSON,nullable= True, default={}),description="组成（JSON格式：药材名称和用量）")
    preparation_method: Optional[str] = Field(default=None, description="制法")
    usage_dosage: Optional[str] = Field(default=None, description="用法用量")
    indication: Optional[str] = Field(default=None, description="主治")
    syndrome_adaptation: Optional[str] = Field(default=None, description="证候适应")
    contraindications: Optional[str] = Field(default=None, description="禁忌")
    modifications: Optional[str] = Field(default=None, description="加减变化")
    clinical_notes: Optional[str] = Field(default=None, description="临床运用")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_prescriptions_name", "name"),
        Index("idx_prescriptions_source", "source"),
        Index("idx_prescriptions_category", "category"),
        Index("idx_prescriptions_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class ClassicText(SQLModel, table=True):
    """古籍条文模型"""
    __tablename__ = "classic_texts"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="条文ID")
    title: str = Field(max_length=100, description="古籍名称")
    chapter: Optional[str] = Field(default=None, max_length=100, description="章节")
    section: Optional[str] = Field(default=None, max_length=100, description="节")
    article_number: Optional[str] = Field(default=None, max_length=20, description="条文编号")
    content: str = Field(description="条文内容")
    translation: Optional[str] = Field(default=None, description="现代译文")
    annotation: Optional[str] = Field(default=None, description="注释")
    clinical_application: Optional[str] = Field(default=None, description="临床应用")
    related_syndromes: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable= True, default={}), description="相关证型（JSON格式）")
    related_prescriptions: Optional[Dict[str, str]] = Field(sa_column=Column(JSON,nullable= True, default={}), description="相关方剂（JSON格式）")
    source_url: Optional[str] = Field(default=None, max_length=255, description="来源链接")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_classic_texts_title", "title"),
        Index("idx_classic_texts_chapter", "chapter"),
        Index("idx_classic_texts_article_number", "article_number"),
        Index("idx_classic_texts_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


