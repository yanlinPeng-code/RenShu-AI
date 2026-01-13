from typing import TypeVar, Generic, Optional, Union, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
from pydantic import field_validator

T = TypeVar('T')

class PaginationInfo(BaseModel):
    """分页信息"""

    page: int = Field(description="当前页码", ge=1)
    page_size: int = Field(description="每页大小", ge=1, le=1000)
    total: int = Field(description="总记录数", ge=0)
    total_pages: int = Field(description="总页数", ge=0)
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")

    @model_validator(mode='after')
    def calculate_fields(self) -> 'PaginationInfo':
        # 计算总页数
        if self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 0
            
        # 计算是否有下一页
        self.has_next = self.page < self.total_pages
        
        # 计算是否有上一页
        self.has_prev = self.page > 1
        
        return self


class PaginatedData(BaseModel, Generic[T]):
    """分页数据"""

    items: List[T] = Field(description="数据列表")
    pagination: PaginationInfo = Field(description="分页信息")