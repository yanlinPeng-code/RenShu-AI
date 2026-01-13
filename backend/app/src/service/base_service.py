from typing import Generic, TypeVar, Type, Optional, Any, Annotated
from uuid import UUID
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import Select, func
from sqlalchemy import delete as sa_delete

from app.src.response.utils import paginated

ModelType=TypeVar("ModelType", bound=SQLModel)

class BaseService(Generic[ModelType]):
    """
    基础crud服务类，
    使用泛型支持多种sqlmodel模型类

    Attributes:
        model (Type(modelType)):概念的数据库模型类
        session (AsyncSession):异步会话类。



    """
    def __init__(self,model:Type[ModelType],session:AsyncSession):
        self.model=model
        self.session=session


    async def create(self,object_in:ModelType)->ModelType:
        """
        创建数据

        Args:
            object_in (ModelType):模型对象

        Returns:
            ModelType:模型对象
        """
        self.session.add(object_in)
        await self.session.flush()
        await self.session.refresh(object_in)
        return object_in


    async def get(self,id:UUID|str)->Optional[ModelType]:
        """
        根据主键的id获取模型实例，


        Args:
            id:int:对象的id
        Returns:
              None或者从数据库映射的数据

        """

        return await self.session.get(self.model,id)


    async def delete(self,onj_in:ModelType)->None:
        """
        根据主键的id删除模型实例，


        Args:
            onj_in:ModelType 删除对象的实例
        Returns:
              None

        """
        await self.session.delete(onj_in)
        await self.session.flush()



    async def update(self,obj_in:ModelType)->ModelType:
        """
        根据主键的id更新模型实例，


        Args:
            obj_in:ModelType:包含更新对象的实例
        Returns:
              None或者从数据库映射的数据

        """

        self.session.add(obj_in)
        await self.session.flush()
        await self.session.refresh(obj_in)
        return obj_in

    async def delete_by_ids(self,ids:list[int])->None:
        """
        高性能批量删除模型实例
        此方法执行单条DELETE ... WhERE id IN (...)SQL语句，性能高，绕过ORM事件

        Args:
            ids:模型实例的id列表
        Returns:
            None
        """
        if not ids:
            return
        pk_col = next(iter(self.model.__table__.primary_key.columns))
        stmt = sa_delete(self.model).where(pk_col.in_(ids))
        await self.session.exec(stmt)
        await self.session.flush()

    async def page_query(self,
                         query: Select,
                         pageNumber: int,
                         pageSize: int,
                         total: Optional[int] = None) -> Any:
        """
        通用的分页查询器
        Args:
            query:(Select):构建好的select语句。
            page_number: 当前页码
            page_size: 每页数量
            total: 可选的计算好的总数
        """
        if total is None:
            #获取主键用于计数，如果没有主键使用第一列
            pk_col = next(iter(self.model.__table__.primary_key.columns),list(self.model.__table__.columns)[0])
            # count_query=select(func.count(pk_col)).select_from(query.subquery())
            count_query = select(func.count(func.distinct(pk_col))).select_from(query.subquery())
            total_result=await self.session.exec(count_query)
            total=total_result.one()


            paginated_query=query.offset(pageSize*(pageNumber-1)).limit(pageSize)


            result=await self.session.exec(paginated_query)

            rows=result.all()

            #TODO返回结果
            return  paginated(
                items=rows,
                page=pageNumber,
                page_size=pageSize,
                total=total,

            )































