"""
数据库迁移脚本：从单表 users 迁移到三端分离的 accounts 表结构

迁移步骤：
1. 创建新表：accounts, patients, doctors, admins, account_refresh_tokens
2. 迁移数据：users -> accounts + (patients/doctors/admins)
3. 迁移 refresh_tokens -> account_refresh_tokens
4. 删除旧表：users, refresh_tokens（可选，建议先保留备份）

使用方法：
python migrate_to_accounts.py
"""
import sys
from uuid import uuid4
from datetime import datetime
import pathlib
current_path=pathlib.Path(__file__).parent.parent


sys.path.insert(0,str(current_path))
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select


from backend.app.src.common.config.prosgresql_config import async_db_manager


# 导入新旧模型
from app.src.model.user_model import User, RefreshToken
from app.src.model.account_model import (
    Account, Patient, Doctor, Admin, AccountRefreshToken
)


async def migrate_users_to_accounts(session: AsyncSession):
    """
    迁移用户数据到新的账户表结构

    users -> accounts + (patients/doctors/admins)
    """
    print("开始迁移用户数据...")

    # 查询所有用户
    result = await session.exec(select(User))
    users = result.all()

    migrated_count = {
        'patient': 0,
        'doctor': 0,
        'admin': 0
    }

    for user in users:
        # 创建 Account 记录
        account = Account(
            id=user.id,  # 保持原有 ID
            email=user.email,
            password_hash=user.password_hash,
            account_type=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        session.add(account)

        # 根据角色创建对应的 profile 记录
        if user.role == 'patient':
            patient = Patient(
                id=uuid4(),
                account_id=user.id,
                username=user.username,
                real_name=user.real_name,
                phone=user.phone,
                gender=user.gender,
                birth_date=user.birth_date,
                constitution_type=user.constitution_type,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            session.add(patient)
            migrated_count['patient'] += 1

        elif user.role == 'doctor':
            doctor = Doctor(
                id=uuid4(),
                account_id=user.id,
                username=user.username,
                real_name=user.real_name,
                phone=user.phone,
                gender=user.gender,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            session.add(doctor)
            migrated_count['doctor'] += 1

        elif user.role == 'admin':
            admin = Admin(
                id=uuid4(),
                account_id=user.id,
                username=user.username,
                avatar_url=user.avatar_url,
                admin_level='admin',
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            session.add(admin)
            migrated_count['admin'] += 1

    await session.commit()

    print(f"用户数据迁移完成:")
    print(f"  - 患者: {migrated_count['patient']} 条")
    print(f"  - 医生: {migrated_count['doctor']} 条")
    print(f"  - 管理员: {migrated_count['admin']} 条")


async def migrate_refresh_tokens(session: AsyncSession):
    """
    迁移刷新令牌数据

    refresh_tokens -> account_refresh_tokens
    """
    print("\n开始迁移刷新令牌数据...")

    # 查询所有刷新令牌
    result = await session.exec(select(RefreshToken))
    tokens = result.all()

    migrated_count = 0

    for token in tokens:
        account_token = AccountRefreshToken(
            id=token.id,
            account_id=token.user_id,  # user_id -> account_id
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            created_at=token.created_at,
            is_revoked=token.is_revoked
        )
        session.add(account_token)
        migrated_count += 1

    await session.commit()

    print(f"刷新令牌数据迁移完成: {migrated_count} 条")


async def main():
    """主迁移流程"""
    # 数据库连接配置（请根据实际情况修改）

    async with async_db_manager.get_session() as session:
        try:
            # 步骤1: 迁移用户数据
            await migrate_users_to_accounts(session)

            # 步骤2: 迁移刷新令牌数据
            await migrate_refresh_tokens(session)

            print("\n✅ 数据迁移成功完成！")
            print("\n⚠️  注意事项：")
            print("1. 请验证新表中的数据是否正确")
            print("2. 确认应用程序使用新表结构正常运行后，再删除旧表")
            print("3. 建议先备份旧表：")
            print("   CREATE TABLE users_backup AS SELECT * FROM users;")
            print("   CREATE TABLE refresh_tokens_backup AS SELECT * FROM refresh_tokens;")

        except Exception as e:
            print(f"\n❌ 迁移失败: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
