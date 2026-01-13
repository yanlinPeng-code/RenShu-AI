import asyncio
from typing import Optional, List
from pgvector.sqlalchemy import Vector
from sqlmodel import SQLModel, Field, create_engine, select, Session

from sqlalchemy import text, Column
from langchain_postgres import PGVectorStore, PGEngine
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import uuid
import json

# 替换为你的settings路径
from app.src.common.config.setting_config import settings

# --------------------------
# 全局配置
# --------------------------
CONFIG = {
    # 数据库配置
    "postgres_user": "postgres",
    "postgres_password": "200124",
    "postgres_host": "localhost",
    "postgres_port": "5432",
    "postgres_db": "test",
    "table_name": "user",
    "schema_name": "public",
    # 字段配置
    "id_column": "id",
    "text_column": "name",
    "vector_column": "name_embedding",
    "vector_size": 1536,
    # 其他配置
    "echo_sql": True,
    "test_data": [
        {"name": "张三", "age": 30, "city": "北京"},
        {"name": "李四", "age": 25, "city": "上海"},
        {"name": "王五", "age": 40, "city": "广州"},
        {"name": "张三丰", "age": 120, "city": "武当山"},
        {"name": "张无忌", "age": 28, "city": "明教总坛"},
        {"name": "李时珍", "age": 56, "city": "黄州"},
        {"name": "张仲景", "age": 65, "city": "南阳"},
        {"name": "刘德华", "age": 62, "city": "香港"},
    ]
}


# --------------------------
# SQLModel模型定义
# --------------------------
class User(SQLModel, table=True):
    __tablename__ = CONFIG['table_name']
    __table_args__ = {"schema": CONFIG['schema_name']}

    id: Optional[uuid.UUID] = Field(
        default=uuid.uuid4,
        primary_key=True,
        nullable=True,
        sa_column_kwargs={
            "server_default": text("uuid_generate_v4()"),  # 数据库层面默认生成UUID
        }
    )
    name: str = Field(max_length=100)
    age: Optional[int] = None
    city: Optional[str] = Field(max_length=100)
    name_embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(1536)))# change embedding size according to model used


# --------------------------
# 工具函数：构建连接字符串
# --------------------------
def get_connection_string() -> str:
    return (
        f"postgresql://{CONFIG['postgres_user']}:{CONFIG['postgres_password']}@"
        f"{CONFIG['postgres_host']}:{CONFIG['postgres_port']}/{CONFIG['postgres_db']}"
    )


def get_async_connection_string() -> str:
    return (
        f"postgresql+asyncpg://{CONFIG['postgres_user']}:{CONFIG['postgres_password']}@"
        f"{CONFIG['postgres_host']}:{CONFIG['postgres_port']}/{CONFIG['postgres_db']}"
    )


# --------------------------
# 步骤1：创建用户表（含UUID主键和向量列）
# --------------------------
async def create_user_table(engine,sync_engine):
    print("\n" + "=" * 40)
    print("步骤1：创建用户表及依赖扩展（UUID+pgvector）")
    print("=" * 40)

    # 1.1 安装必要扩展（pgvector+uuid-ossp）
    print("\n1.1 检查必要扩展...")
    try:
        async with engine.connect() as conn:
            # 安装UUID生成扩展
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            # 安装向量扩展
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.commit()

            # 验证扩展
            uuid_ext_result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'uuid-ossp';"))
            vector_ext_result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))

            uuid_ext = uuid_ext_result.first()
            vector_ext = vector_ext_result.first()

            if not uuid_ext:
                raise Exception("uuid-ossp扩展安装失败，请手动执行：CREATE EXTENSION \"uuid-ossp\";")
            if not vector_ext:
                raise Exception("pgvector扩展安装失败，请手动执行：CREATE EXTENSION vector;")
            print("✅ UUID和pgvector扩展已就绪")
    except Exception as e:
        print(f"❌ 扩展处理失败：{e}")
        return False

    # 1.2 创建表结构
    print(f"\n1.2 创建表 {CONFIG['schema_name']}.{CONFIG['table_name']}...")
    try:
        SQLModel.metadata.create_all(sync_engine)
        print(f"✅ 表 {CONFIG['table_name']} 创建成功")
    except Exception as e:
        print(f"❌ 表创建失败：{e}")
        return False

    # 1.3 验证表结构
    print("\n1.3 验证表结构...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{CONFIG['table_name']}' AND table_schema = '{CONFIG['schema_name']}';
            """))
            columns = {row[0]: row[1] for row in result.fetchall()}
            required = [CONFIG['id_column'], CONFIG['text_column'], 'age', 'city', 'name_embedding']
            missing = [col for col in required if col not in columns]
            if missing:
                raise Exception(f"缺少必要字段：{missing}")

            # 验证UUID类型
            if columns[CONFIG['id_column']] != 'uuid':
                raise Exception(f"id字段类型错误（预期uuid，实际{columns[CONFIG['id_column']]}）")

            print("✅ 表结构验证通过")
            return True
    except Exception as e:
        print(f"❌ 表结构验证失败：{e}")
        return False


# --------------------------
# 步骤2：插入测试数据
# --------------------------
async def insert_test_data(engine):
    print("\n" + "=" * 40)
    print("步骤2：插入测试数据（UUID自动生成）")
    print("=" * 40)

    # 2.1 检查表中是否已有数据
    print("\n2.1 检查现有数据...")
    async with engine.connect() as conn:
        result = await conn.execute(text(f"SELECT COUNT(*) FROM {CONFIG['schema_name']}.{CONFIG['table_name']};"))
        count = result.scalar()
        if count > 0:
            print(f"ℹ️  表中已有 {count} 条数据，是否继续插入？（y/N）")
            if input().strip().lower() != 'y':
                print("ℹ️  跳过数据插入")
                return True

    # 2.2 插入测试数据
    print(f"\n2.2 插入 {len(CONFIG['test_data'])} 条测试数据...")
    try:
        async with engine.connect() as conn:
            for data in CONFIG['test_data']:
                insert_sql = f"""
                INSERT INTO {CONFIG['schema_name']}.{CONFIG['table_name']} (name, age, city)
                VALUES (:name, :age, :city);
                """
                await conn.execute(text(insert_sql), data)
            await conn.commit()
        print("✅ 数据插入完成（UUID自动生成）")
    except Exception as e:
        print(f"❌ 数据插入失败：{e}")
        return False

    # 2.3 验证插入结果
    print("\n2.3 验证插入结果...")
    try:
        async with engine.connect() as conn:
            names = [d['name'] for d in CONFIG['test_data']]
            name_placeholders = [name.replace("'", "''") for name in names]
            placeholders_str = "', '".join(name_placeholders)
            result = await conn.execute(text(f"""
                SELECT id, name, age, city 
                FROM {CONFIG['schema_name']}.{CONFIG['table_name']} 
                WHERE name IN ('{placeholders_str}')
                LIMIT {len(names)};
            """))
            inserted = result.fetchall()
            if len(inserted) != len(CONFIG['test_data']):
                raise Exception(f"插入不完整（预期{len(CONFIG['test_data'])}条，实际{len(inserted)}条）")

            print("插入的数据预览（只显示前3条的ID前缀）：")
            for row in inserted[:3]:
                uuid_prefix = str(row[0])[:8]
                print(f"  - ID: {uuid_prefix}... | 姓名: {row[1]} | 年龄: {row[2]} | 城市: {row[3]}")
            print("✅ 数据验证通过")
            return True
    except Exception as e:
        print(f"❌ 数据验证失败：{e}")
        return False


# --------------------------
# 步骤3：生成嵌入并存储
# --------------------------
async def generate_embeddings(engine):
    print("\n" + "=" * 40)
    print("步骤3：生成name字段的嵌入向量")
    print("=" * 40)

    # 3.1 初始化OpenAI嵌入模型
    print("\n3.1 初始化嵌入模型...")
    try:
        embedding = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        # 验证模型维度
        test_vec = embedding.embed_query("测试")
        if len(test_vec) != CONFIG['vector_size']:
            raise Exception(f"模型维度错误（预期{CONFIG['vector_size']}，实际{len(test_vec)}）")
        print("✅ 嵌入模型初始化成功")
    except Exception as e:
        print(f"❌ 模型初始化失败：{e}")
        return False, None

    # 3.2 读取数据并生成嵌入
    print("\n3.2 读取数据并生成嵌入...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(f"""
                SELECT id, name 
                FROM {CONFIG['schema_name']}.{CONFIG['table_name']};
            """))
            # UUID在数据库中读取后为字符串类型，直接使用
            users = [{"id": row[0], "name": row[1]} for row in result.fetchall()]
        if not users:
            raise Exception("表中无数据，无法生成嵌入")
        print(f"找到 {len(users)} 条数据，开始生成嵌入...")

        # UUID为字符串，直接作为Document的id（无需类型转换）
        docs = [Document(id=str(u['id']), page_content=u['name']) for u in users]

        # 创建向量存储
        pg_engine = PGEngine.from_engine(engine)
        store = await PGVectorStore.create(
            engine=pg_engine,
            table_name=CONFIG['table_name'],
            schema_name=CONFIG['schema_name'],
            embedding_service=embedding,
            content_column=CONFIG['text_column'],
            embedding_column='name_embedding',
            id_column=CONFIG['id_column'],
        )

        # 添加文档到向量存储
        await store.aadd_documents(docs)
        print(f"✅ 已为 {len(users)} 条数据生成嵌入，存储到 name_embedding 列")
        return True, store
    except Exception as e:
        print(f"❌ 嵌入生成失败：{e}")
        return False, None


# --------------------------
# 步骤4：测试相似查询
# --------------------------
async def test_similarity_search(store: PGVectorStore, engine):
    print("\n" + "=" * 40)
    print("步骤4：测试相似姓名查询")
    print("=" * 40)

    # 4.1 执行查询
    queries = ["张", "李", "医生相关"]
    for query in queries:
        print(f"\n4.1 查询：找名字与「{query}」相似的用户")
        try:
            similar_docs = await store.asimilarity_search(query, k=2)
            if not similar_docs:
                print("  ❌ 未找到相似结果")
                continue

            # 4.2 查询完整用户信息
            for i, doc in enumerate(similar_docs, 1):
                async with engine.connect() as conn:
                    result = await conn.execute(text(f"""
                        SELECT * FROM {CONFIG['schema_name']}.{CONFIG['table_name']} 
                        WHERE id = :id;
                    """), {"id": doc.id})
                    user = result.mappings().first()

                if user:
                    uuid_prefix = str(doc.id)[:8]
                    print(
                        f"  {i}. ID: {uuid_prefix}... | 姓名: {doc.page_content} | 年龄: {user['age']} | 城市: {user['city']}")
        except Exception as e:
            print(f"  ❌ 查询失败：{e}")

    print("\n✅ 相似查询测试完成")
    return True


# --------------------------
# 主函数：按流程执行所有步骤
# --------------------------
async def main():
    print("=" * 60)
    print("【用户表向量嵌入全流程（SQLModel异步版）】开始执行")
    print("=" * 60)

    # 初始化数据库连接
    print("\n初始化数据库连接...")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.engine import create_engine
        sync_engine = create_engine(
            get_connection_string(),
            echo=CONFIG["echo_sql"],
            pool_size=20,
            max_overflow=0,
            pool_recycle=3600
        )
        engine = create_async_engine(
            get_async_connection_string(),
            echo=CONFIG["echo_sql"],
            pool_size=20,
            max_overflow=0,
            pool_recycle=3600
        )
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        return

    # 按顺序执行步骤
    if not await create_user_table(engine,sync_engine):
        await engine.dispose()
        return

    if not await insert_test_data(engine):
        await engine.dispose()
        return

    emb_result, store = await generate_embeddings(engine)
    if not emb_result or not store:
        await engine.dispose()
        return

    await test_similarity_search(store, engine)

    # 清理资源
    await engine.dispose()
    print("\n" + "=" * 60)
    print("【用户表向量嵌入全流程（SQLModel异步版）】执行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())



