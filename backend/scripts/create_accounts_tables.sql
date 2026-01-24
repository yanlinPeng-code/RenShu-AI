-- 三端分离表结构 SQL 脚本
-- 创建新的 accounts 表结构

-- 1. 创建 accounts 表（基础认证表）
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('patient', 'doctor', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_accounts_email_type UNIQUE (email, account_type)
);

CREATE INDEX idx_accounts_email ON accounts(email);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- 2. 创建 patients 表（患者信息表）
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL UNIQUE REFERENCES accounts(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL UNIQUE,
    real_name VARCHAR(50),
    phone VARCHAR(20),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    birth_date DATE,
    constitution_type VARCHAR(50),
    avatar_url VARCHAR(255),
    medical_history TEXT,
    family_history TEXT,
    allergy_info TEXT,
    current_medications TEXT,
    emergency_contact_name VARCHAR(50),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patients_username ON patients(username);
CREATE INDEX idx_patients_account_id ON patients(account_id);

-- 3. 创建 doctors 表（医生信息表）
CREATE TABLE IF NOT EXISTS doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL UNIQUE REFERENCES accounts(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL UNIQUE,
    real_name VARCHAR(50),
    phone VARCHAR(20),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    avatar_url VARCHAR(255),
    license_no VARCHAR(50),
    department VARCHAR(50),
    hospital VARCHAR(100),
    specialty VARCHAR(100),
    title VARCHAR(50),
    introduction TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doctors_username ON doctors(username);
CREATE INDEX idx_doctors_account_id ON doctors(account_id);
CREATE INDEX idx_doctors_license_no ON doctors(license_no);

-- 4. 创建 admins 表（管理员信息表）
CREATE TABLE IF NOT EXISTS admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL UNIQUE REFERENCES accounts(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL UNIQUE,
    avatar_url VARCHAR(255),
    admin_level VARCHAR(20) DEFAULT 'admin' CHECK (admin_level IN ('admin', 'super_admin')),
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admins_username ON admins(username);
CREATE INDEX idx_admins_account_id ON admins(account_id);

-- 5. 创建 account_refresh_tokens 表（刷新令牌表）
CREATE TABLE IF NOT EXISTS account_refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_account_refresh_tokens_account_id ON account_refresh_tokens(account_id);
CREATE INDEX idx_account_refresh_tokens_token_hash ON account_refresh_tokens(token_hash);
CREATE INDEX idx_account_refresh_tokens_expires_at ON account_refresh_tokens(expires_at);

-- 6. 创建 account_activities 表（账户活动记录表）
CREATE TABLE IF NOT EXISTS account_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    activity_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_account_activities_account_id ON account_activities(account_id);
CREATE INDEX idx_account_activities_type ON account_activities(activity_type);
CREATE INDEX idx_account_activities_created_at ON account_activities(created_at);

-- 7. 添加注释
COMMENT ON TABLE accounts IS '账户基础表 - 存储所有账户的认证信息';
COMMENT ON TABLE patients IS '患者信息表 - 存储患者端特有信息';
COMMENT ON TABLE doctors IS '医生信息表 - 存储医生端特有信息';
COMMENT ON TABLE admins IS '管理员信息表 - 存储管理员端特有信息';
COMMENT ON TABLE account_refresh_tokens IS '账户刷新令牌表';
COMMENT ON TABLE account_activities IS '账户活动记录表';

COMMENT ON COLUMN accounts.account_type IS '账户类型: patient/doctor/admin';
COMMENT ON CONSTRAINT uq_accounts_email_type ON accounts IS '同一邮箱可以注册不同端的账号';
