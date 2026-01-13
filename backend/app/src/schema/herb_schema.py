from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlmodel import SQLModel


# # 创建和更新模型
# class HerbCreate(BaseModel):
#     """药材创建模型"""
#
#     name: str = Field(description="药材名称")
#     pinyin: Optional[str] = Field(default=None, description="拼音")
#     latin_name: Optional[str] = Field(default=None, description="拉丁学名")
#     category: Optional[str] = Field(default=None, description="药材分类")
#     nature: Optional[str] = Field(default=None, description="药性（寒、热、温、凉、平）")
#     flavor: Optional[str] = Field(default=None, description="五味（辛、甘、酸、苦、咸）")
#     meridian: Optional[str] = Field(default=None, description="归经")
#     effect: Optional[str] = Field(default=None, description="功效")
#     indication: Optional[str] = Field(default=None, description="主治")
#     usage_dosage: Optional[str] = Field(default=None, description="用法用量")
#     contraindications: Optional[str] = Field(default=None, description="禁忌")
#     incompatibilities: Optional[str] = Field(default=None, description="配伍禁忌（十八反、十九畏等）")
#     processing_method: Optional[str] = Field(default=None, description="炮制方法")
#     storage_method: Optional[str] = Field(default=None, description="贮藏方法")
#
#     @field_validator('nature')
#     def validate_nature(cls, v):
#         """验证药性"""
#         if v is not None:
#             allowed_natures = ['寒', '热', '温', '凉', '平']
#             if v not in allowed_natures:
#                 raise ValueError(f'药性必须是以下之一: {", ".join(allowed_natures)}')
#         return v
#
#     @field_validator('flavor')
#     def validate_flavor(cls, v):
#         """验证五味"""
#         if v is not None:
#             allowed_flavors = ['辛', '甘', '酸', '苦', '咸']
#             if v not in allowed_flavors:
#                 raise ValueError(f'五味必须是以下之一: {", ".join(allowed_flavors)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class HerbUpdate(BaseModel):
#     """药材更新模型"""
#
#     name: Optional[str] = Field(default=None, description="药材名称")
#     pinyin: Optional[str] = Field(default=None, description="拼音")
#     latin_name: Optional[str] = Field(default=None, description="拉丁学名")
#     category: Optional[str] = Field(default=None, description="药材分类")
#     nature: Optional[str] = Field(default=None, description="药性（寒、热、温、凉、平）")
#     flavor: Optional[str] = Field(default=None, description="五味（辛、甘、酸、苦、咸）")
#     meridian: Optional[str] = Field(default=None, description="归经")
#     effect: Optional[str] = Field(default=None, description="功效")
#     indication: Optional[str] = Field(default=None, description="主治")
#     usage_dosage: Optional[str] = Field(default=None, description="用法用量")
#     contraindications: Optional[str] = Field(default=None, description="禁忌")
#     incompatibilities: Optional[str] = Field(default=None, description="配伍禁忌（十八反、十九畏等）")
#     processing_method: Optional[str] = Field(default=None, description="炮制方法")
#     storage_method: Optional[str] = Field(default=None, description="贮藏方法")
#     is_active: Optional[bool] = Field(default=None, description="是否启用")
#
#     @field_validator('nature')
#     def validate_nature(cls, v):
#         """验证药性"""
#         if v is not None:
#             allowed_natures = ['寒', '热', '温', '凉', '平']
#             if v not in allowed_natures:
#                 raise ValueError(f'药性必须是以下之一: {", ".join(allowed_natures)}')
#         return v
#
#     @field_validator('flavor')
#     def validate_flavor(cls, v):
#         """验证五味"""
#         if v is not None:
#             allowed_flavors = ['辛', '甘', '酸', '苦', '咸']
#             if v not in allowed_flavors:
#                 raise ValueError(f'五味必须是以下之一: {", ".join(allowed_flavors)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class HerbInventoryCreate(BaseModel):
#     """药材库存创建模型"""
#
#     herb_id: int = Field(description="药材ID")
#     batch_number: Optional[str] = Field(default=None, description="批次号")
#     supplier: Optional[str] = Field(default=None, description="供应商")
#     purchase_date: Optional[date] = Field(default=None, description="采购日期")
#     expiry_date: Optional[date] = Field(default=None, description="过期日期")
#     quantity: Decimal = Field(description="库存数量")
#     unit: str = Field(description="单位（克、千克等）")
#     unit_price: Optional[Decimal] = Field(default=None, description="单价")
#     quality_grade: Optional[str] = Field(default=None, description="质量等级")
#     storage_location: Optional[str] = Field(default=None, description="存储位置")
#
#     @field_validator('quantity')
#     def validate_quantity(cls, v):
#         """验证数量"""
#         if v < 0:
#             raise ValueError('库存数量不能为负数')
#         return v
#
#     model_config = ConfigDict(
#         json_encoders={
#             date: lambda v: v.isoformat(),
#             Decimal: lambda v: float(v)
#         },
#         populate_by_name=True
#     )
#
#
# class HerbInventoryUpdate(BaseModel):
#     """药材库存更新模型"""
#
#     batch_number: Optional[str] = Field(default=None, description="批次号")
#     supplier: Optional[str] = Field(default=None, description="供应商")
#     purchase_date: Optional[date] = Field(default=None, description="采购日期")
#     expiry_date: Optional[date] = Field(default=None, description="过期日期")
#     quantity: Optional[Decimal] = Field(default=None, description="库存数量")
#     unit: Optional[str] = Field(default=None, description="单位（克、千克等）")
#     unit_price: Optional[Decimal] = Field(default=None, description="单价")
#     quality_grade: Optional[str] = Field(default=None, description="质量等级")
#     storage_location: Optional[str] = Field(default=None, description="存储位置")
#     status: Optional[str] = Field(default=None, description="库存状态")
#
#     @field_validator('status')
#     def validate_status(cls, v):
#         """验证库存状态"""
#         if v is not None:
#             allowed_statuses = ['available', 'low_stock', 'out_of_stock', 'expired']
#             if v not in allowed_statuses:
#                 raise ValueError(f'库存状态必须是以下之一: {", ".join(allowed_statuses)}')
#         return v
#
#     @field_validator('quantity')
#     def validate_quantity(cls, v):
#         """验证数量"""
#         if v is not None and v < 0:
#             raise ValueError('库存数量不能为负数')
#         return v
#
#     model_config = ConfigDict(
#         json_encoders={
#             date: lambda v: v.isoformat(),
#             Decimal: lambda v: float(v)
#         },
#         populate_by_name=True
#     )
#
#
# class PrescriptionCreate(BaseModel):
#     """方剂创建模型"""
#
#     name: str = Field(description="方剂名称")
#     source: Optional[str] = Field(default=None, description="出处（如：《伤寒论》、《金匮要略》等）")
#     category: Optional[str] = Field(default=None, description="方剂分类")
#     composition: str = Field(description="组成（JSON格式：药材名称和用量）")
#     preparation_method: Optional[str] = Field(default=None, description="制法")
#     usage_dosage: Optional[str] = Field(default=None, description="用法用量")
#     indication: Optional[str] = Field(default=None, description="主治")
#     syndrome_adaptation: Optional[str] = Field(default=None, description="证候适应")
#     contraindications: Optional[str] = Field(default=None, description="禁忌")
#     modifications: Optional[str] = Field(default=None, description="加减变化")
#     clinical_notes: Optional[str] = Field(default=None, description="临床运用")
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class PrescriptionUpdate(BaseModel):
#     """方剂更新模型"""
#
#     name: Optional[str] = Field(default=None, description="方剂名称")
#     source: Optional[str] = Field(default=None, description="出处（如：《伤寒论》、《金匮要略》等）")
#     category: Optional[str] = Field(default=None, description="方剂分类")
#     composition: Optional[str] = Field(default=None, description="组成（JSON格式：药材名称和用量）")
#     preparation_method: Optional[str] = Field(default=None, description="制法")
#     usage_dosage: Optional[str] = Field(default=None, description="用法用量")
#     indication: Optional[str] = Field(default=None, description="主治")
#     syndrome_adaptation: Optional[str] = Field(default=None, description="证候适应")
#     contraindications: Optional[str] = Field(default=None, description="禁忌")
#     modifications: Optional[str] = Field(default=None, description="加减变化")
#     clinical_notes: Optional[str] = Field(default=None, description="临床运用")
#     is_active: Optional[bool] = Field(default=None, description="是否启用")
#
#     model_config = ConfigDict(populate_by_name=True)

class HerbCreate(SQLModel):
    """药材创建模型"""

    name: str = Field(description="药材名称")
    pinyin: Optional[str] = Field(default=None, description="拼音")
    latin_name: Optional[str] = Field(default=None, description="拉丁学名")
    category: Optional[str] = Field(default=None, description="药材分类")
    nature: Optional[str] = Field(default=None, description="药性（寒、热、温、凉、平）")
    flavor: Optional[str] = Field(default=None, description="五味（辛、甘、酸、苦、咸）")
    meridian: Optional[str] = Field(default=None, description="归经")
    effect: Optional[str] = Field(default=None, description="功效")
    indication: Optional[str] = Field(default=None, description="主治")
    usage_dosage: Optional[str] = Field(default=None, description="用法用量")
    contraindications: Optional[str] = Field(default=None, description="禁忌")
    incompatibilities: Optional[str] = Field(default=None, description="配伍禁忌（十八反、十九畏等）")
    processing_method: Optional[str] = Field(default=None, description="炮制方法")
    storage_method: Optional[str] = Field(default=None, description="贮藏方法")

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

    model_config = ConfigDict(populate_by_name=True)


class HerbUpdate(SQLModel):
    """药材更新模型"""

    name: Optional[str] = Field(default=None, description="药材名称")
    pinyin: Optional[str] = Field(default=None, description="拼音")
    latin_name: Optional[str] = Field(default=None, description="拉丁学名")
    category: Optional[str] = Field(default=None, description="药材分类")
    nature: Optional[str] = Field(default=None, description="药性（寒、热、温、凉、平）")
    flavor: Optional[str] = Field(default=None, description="五味（辛、甘、酸、苦、咸）")
    meridian: Optional[str] = Field(default=None, description="归经")
    effect: Optional[str] = Field(default=None, description="功效")
    indication: Optional[str] = Field(default=None, description="主治")
    usage_dosage: Optional[str] = Field(default=None, description="用法用量")
    contraindications: Optional[str] = Field(default=None, description="禁忌")
    incompatibilities: Optional[str] = Field(default=None, description="配伍禁忌（十八反、十九畏等）")
    processing_method: Optional[str] = Field(default=None, description="炮制方法")
    storage_method: Optional[str] = Field(default=None, description="贮藏方法")
    is_active: Optional[bool] = Field(default=None, description="是否启用")

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

    model_config = ConfigDict(populate_by_name=True)


class HerbInventoryCreate(SQLModel):
    """药材库存创建模型"""

    herb_id: int = Field(description="药材ID")
    batch_number: Optional[str] = Field(default=None, description="批次号")
    supplier: Optional[str] = Field(default=None, description="供应商")
    purchase_date: Optional[date] = Field(default=None, description="采购日期")
    expiry_date: Optional[date] = Field(default=None, description="过期日期")
    quantity: Decimal = Field(description="库存数量")
    unit: str = Field(description="单位（克、千克等）")
    unit_price: Optional[Decimal] = Field(default=None, description="单价")
    quality_grade: Optional[str] = Field(default=None, description="质量等级")
    storage_location: Optional[str] = Field(default=None, description="存储位置")

    @field_validator('quantity')
    def validate_quantity(cls, v):
        """验证数量"""
        if v < 0:
            raise ValueError('库存数量不能为负数')
        return v

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )


class HerbInventoryUpdate(SQLModel):
    """药材库存更新模型"""

    batch_number: Optional[str] = Field(default=None, description="批次号")
    supplier: Optional[str] = Field(default=None, description="供应商")
    purchase_date: Optional[date] = Field(default=None, description="采购日期")
    expiry_date: Optional[date] = Field(default=None, description="过期日期")
    quantity: Optional[Decimal] = Field(default=None, description="库存数量")
    unit: Optional[str] = Field(default=None, description="单位（克、千克等）")
    unit_price: Optional[Decimal] = Field(default=None, description="单价")
    quality_grade: Optional[str] = Field(default=None, description="质量等级")
    storage_location: Optional[str] = Field(default=None, description="存储位置")
    status: Optional[str] = Field(default=None, description="库存状态")

    @field_validator('status')
    def validate_status(cls, v):
        """验证库存状态"""
        if v is not None:
            allowed_statuses = ['available', 'low_stock', 'out_of_stock', 'expired']
            if v not in allowed_statuses:
                raise ValueError(f'库存状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @field_validator('quantity')
    def validate_quantity(cls, v):
        """验证数量"""
        if v is not None and v < 0:
            raise ValueError('库存数量不能为负数')
        return v

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        populate_by_name=True
    )


class PrescriptionCreate(SQLModel):
    """方剂创建模型"""

    name: str = Field(description="方剂名称")
    source: Optional[str] = Field(default=None, description="出处（如：《伤寒论》、《金匮要略》等）")
    category: Optional[str] = Field(default=None, description="方剂分类")
    composition: str = Field(description="组成（JSON格式：药材名称和用量）")
    preparation_method: Optional[str] = Field(default=None, description="制法")
    usage_dosage: Optional[str] = Field(default=None, description="用法用量")
    indication: Optional[str] = Field(default=None, description="主治")
    syndrome_adaptation: Optional[str] = Field(default=None, description="证候适应")
    contraindications: Optional[str] = Field(default=None, description="禁忌")
    modifications: Optional[str] = Field(default=None, description="加减变化")
    clinical_notes: Optional[str] = Field(default=None, description="临床运用")

    model_config = ConfigDict(populate_by_name=True)


class PrescriptionUpdate(SQLModel):
    """方剂更新模型"""

    name: Optional[str] = Field(default=None, description="方剂名称")
    source: Optional[str] = Field(default=None, description="出处（如：《伤寒论》、《金匮要略》等）")
    category: Optional[str] = Field(default=None, description="方剂分类")
    composition: Optional[str] = Field(default=None, description="组成（JSON格式：药材名称和用量）")
    preparation_method: Optional[str] = Field(default=None, description="制法")
    usage_dosage: Optional[str] = Field(default=None, description="用法用量")
    indication: Optional[str] = Field(default=None, description="主治")
    syndrome_adaptation: Optional[str] = Field(default=None, description="证候适应")
    contraindications: Optional[str] = Field(default=None, description="禁忌")
    modifications: Optional[str] = Field(default=None, description="加减变化")
    clinical_notes: Optional[str] = Field(default=None, description="临床运用")
    is_active: Optional[bool] = Field(default=None, description="是否启用")

    model_config = ConfigDict(populate_by_name=True)