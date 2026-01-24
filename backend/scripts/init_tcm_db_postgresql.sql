-- SmartTCM-Agent 中医问诊系统数据库初始化脚本 (PostgreSQL) - UUID版本
-- 创建数据库
CREATE DATABASE tcm_agent_db ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;

-- 连接到数据库
\c tcm_agent_db;

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 用户表 (users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'patient' CHECK (role IN ('patient', 'doctor', 'admin')),
    real_name VARCHAR(50),
    phone VARCHAR(20),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    birth_date DATE,
    constitution_type VARCHAR(50),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.username IS '用户名';
COMMENT ON COLUMN users.email IS '邮箱';
COMMENT ON COLUMN users.password_hash IS '密码哈希';
COMMENT ON COLUMN users.role IS '用户角色';
COMMENT ON COLUMN users.real_name IS '真实姓名';
COMMENT ON COLUMN users.phone IS '手机号';
COMMENT ON COLUMN users.gender IS '性别';
COMMENT ON COLUMN users.birth_date IS '出生日期';
COMMENT ON COLUMN users.constitution_type IS '体质类型（如：阳虚质、阴虚质等）';
COMMENT ON COLUMN users.avatar_url IS '头像URL';
COMMENT ON COLUMN users.is_active IS '是否激活';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间';

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为 users 表创建更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 users 表创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- 2. 患者表 (patients) - 扩展用户信息
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    patient_code VARCHAR(20) UNIQUE NOT NULL,
    medical_history TEXT,
    family_history TEXT,
    allergy_info TEXT,
    current_medications TEXT,
    emergency_contact_name VARCHAR(50),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE patients IS '患者详细信息表';
COMMENT ON COLUMN patients.user_id IS '关联用户ID';
COMMENT ON COLUMN patients.patient_code IS '患者编号';
COMMENT ON COLUMN patients.medical_history IS '既往病史';
COMMENT ON COLUMN patients.family_history IS '家族病史';
COMMENT ON COLUMN patients.allergy_info IS '过敏信息';
COMMENT ON COLUMN patients.current_medications IS '当前用药情况';
COMMENT ON COLUMN patients.emergency_contact_name IS '紧急联系人姓名';
COMMENT ON COLUMN patients.emergency_contact_phone IS '紧急联系人电话';
COMMENT ON COLUMN patients.created_at IS '创建时间';
COMMENT ON COLUMN patients.updated_at IS '更新时间';

-- 为 patients 表创建更新时间触发器
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加外键约束
ALTER TABLE patients ADD CONSTRAINT fk_patients_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 为 patients 表创建索引
CREATE INDEX idx_patients_patient_code ON patients(patient_code);
CREATE INDEX idx_patients_user_id ON patients(user_id);

-- 3. 病例表 (medical_cases)
CREATE TABLE medical_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL,
    case_code VARCHAR(20) UNIQUE NOT NULL,
    chief_complaint TEXT NOT NULL,
    present_illness TEXT,
    symptoms TEXT NOT NULL, -- JSON格式存储
    tongue_description TEXT,
    pulse_description TEXT,
    syndrome_type VARCHAR(100),
    syndrome_confidence DECIMAL(3,2), -- 0-1
    treatment_principle TEXT,
    prescription_name VARCHAR(100),
    prescription_ingredients TEXT, -- JSON格式
    dosage_instruction TEXT,
    precautions TEXT,
    follow_up_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    doctor_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE medical_cases IS '病例表';
COMMENT ON COLUMN medical_cases.patient_id IS '患者ID';
COMMENT ON COLUMN medical_cases.case_code IS '病例编号';
COMMENT ON COLUMN medical_cases.chief_complaint IS '主诉';
COMMENT ON COLUMN medical_cases.present_illness IS '现病史';
COMMENT ON COLUMN medical_cases.symptoms IS '症状描述（JSON格式存储）';
COMMENT ON COLUMN medical_cases.tongue_description IS '舌象描述';
COMMENT ON COLUMN medical_cases.pulse_description IS '脉象描述';
COMMENT ON COLUMN medical_cases.syndrome_type IS '辨证结果（证型）';
COMMENT ON COLUMN medical_cases.syndrome_confidence IS '辨证置信度（0-1）';
COMMENT ON COLUMN medical_cases.treatment_principle IS '治则治法';
COMMENT ON COLUMN medical_cases.prescription_name IS '推荐方剂名称';
COMMENT ON COLUMN medical_cases.prescription_ingredients IS '方剂组成（JSON格式）';
COMMENT ON COLUMN medical_cases.dosage_instruction IS '用法用量';
COMMENT ON COLUMN medical_cases.precautions IS '注意事项';
COMMENT ON COLUMN medical_cases.follow_up_date IS '复诊日期';
COMMENT ON COLUMN medical_cases.status IS '病例状态';
COMMENT ON COLUMN medical_cases.doctor_notes IS '医生备注';
COMMENT ON COLUMN medical_cases.created_at IS '创建时间';
COMMENT ON COLUMN medical_cases.updated_at IS '更新时间';

-- 为 medical_cases 表创建更新时间触发器
CREATE TRIGGER update_medical_cases_updated_at BEFORE UPDATE ON medical_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加外键约束
ALTER TABLE medical_cases ADD CONSTRAINT fk_medical_cases_patient_id FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE;

-- 为 medical_cases 表创建索引
CREATE INDEX idx_medical_cases_patient_id ON medical_cases(patient_id);
CREATE INDEX idx_medical_cases_case_code ON medical_cases(case_code);
CREATE INDEX idx_medical_cases_syndrome_type ON medical_cases(syndrome_type);
CREATE INDEX idx_medical_cases_status ON medical_cases(status);
CREATE INDEX idx_medical_cases_created_at ON medical_cases(created_at);

-- 4. 症状表 (symptoms) - 标准化症状库
CREATE TABLE symptoms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    severity_levels TEXT, -- JSON格式
    related_syndromes TEXT, -- JSON格式
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE symptoms IS '症状库表';
COMMENT ON COLUMN symptoms.name IS '症状名称';
COMMENT ON COLUMN symptoms.category IS '症状分类（如：寒热、汗出、二便等）';
COMMENT ON COLUMN symptoms.description IS '症状描述';
COMMENT ON COLUMN symptoms.severity_levels IS '严重程度分级（JSON格式）';
COMMENT ON COLUMN symptoms.related_syndromes IS '相关证型（JSON格式）';
COMMENT ON COLUMN symptoms.is_active IS '是否启用';
COMMENT ON COLUMN symptoms.created_at IS '创建时间';
COMMENT ON COLUMN symptoms.updated_at IS '更新时间';

-- 为 symptoms 表创建更新时间触发器
CREATE TRIGGER update_symptoms_updated_at BEFORE UPDATE ON symptoms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 symptoms 表创建索引
CREATE INDEX idx_symptoms_name ON symptoms(name);
CREATE INDEX idx_symptoms_category ON symptoms(category);
CREATE INDEX idx_symptoms_is_active ON symptoms(is_active);

-- 5. 证型表 (syndromes) - 中医证型库
CREATE TABLE syndromes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    main_symptoms TEXT, -- JSON格式
    treatment_principle TEXT,
    common_prescriptions TEXT, -- JSON格式
    precautions TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE syndromes IS '证型库表';
COMMENT ON COLUMN syndromes.name IS '证型名称';
COMMENT ON COLUMN syndromes.category IS '证型分类（如：八纲辨证、脏腑辨证等）';
COMMENT ON COLUMN syndromes.description IS '证型描述';
COMMENT ON COLUMN syndromes.main_symptoms IS '主要症状（JSON格式）';
COMMENT ON COLUMN syndromes.treatment_principle IS '治则治法';
COMMENT ON COLUMN syndromes.common_prescriptions IS '常用方剂（JSON格式）';
COMMENT ON COLUMN syndromes.precautions IS '注意事项';
COMMENT ON COLUMN syndromes.is_active IS '是否启用';
COMMENT ON COLUMN syndromes.created_at IS '创建时间';
COMMENT ON COLUMN syndromes.updated_at IS '更新时间';

-- 为 syndromes 表创建更新时间触发器
CREATE TRIGGER update_syndromes_updated_at BEFORE UPDATE ON syndromes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 syndromes 表创建索引
CREATE INDEX idx_syndromes_name ON syndromes(name);
CREATE INDEX idx_syndromes_category ON syndromes(category);
CREATE INDEX idx_syndromes_is_active ON syndromes(is_active);

-- 6. 药材表 (herbs) - 中药材基础信息
CREATE TABLE herbs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    pinyin VARCHAR(100),
    latin_name VARCHAR(100),
    category VARCHAR(50),
    nature VARCHAR(20), -- 寒、热、温、凉、平
    flavor VARCHAR(50), -- 辛、甘、酸、苦、咸
    meridian VARCHAR(100), -- 归经
    effect TEXT,
    indication TEXT,
    usage_dosage TEXT,
    contraindications TEXT,
    incompatibilities TEXT, -- 配伍禁忌（十八反、十九畏等）
    processing_method TEXT,
    storage_method TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE herbs IS '药材表';
COMMENT ON COLUMN herbs.name IS '药材名称';
COMMENT ON COLUMN herbs.pinyin IS '拼音';
COMMENT ON COLUMN herbs.latin_name IS '拉丁学名';
COMMENT ON COLUMN herbs.category IS '药材分类（如：补虚药、清热药等）';
COMMENT ON COLUMN herbs.nature IS '药性（寒、热、温、凉、平）';
COMMENT ON COLUMN herbs.flavor IS '五味（辛、甘、酸、苦、咸）';
COMMENT ON COLUMN herbs.meridian IS '归经';
COMMENT ON COLUMN herbs.effect IS '功效';
COMMENT ON COLUMN herbs.indication IS '主治';
COMMENT ON COLUMN herbs.usage_dosage IS '用法用量';
COMMENT ON COLUMN herbs.contraindications IS '禁忌';
COMMENT ON COLUMN herbs.incompatibilities IS '配伍禁忌（十八反、十九畏等）';
COMMENT ON COLUMN herbs.processing_method IS '炮制方法';
COMMENT ON COLUMN herbs.storage_method IS '贮藏方法';
COMMENT ON COLUMN herbs.is_active IS '是否启用';
COMMENT ON COLUMN herbs.created_at IS '创建时间';
COMMENT ON COLUMN herbs.updated_at IS '更新时间';

-- 为 herbs 表创建更新时间触发器
CREATE TRIGGER update_herbs_updated_at BEFORE UPDATE ON herbs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 herbs 表创建索引
CREATE INDEX idx_herbs_name ON herbs(name);
CREATE INDEX idx_herbs_category ON herbs(category);
CREATE INDEX idx_herbs_nature ON herbs(nature);
CREATE INDEX idx_herbs_is_active ON herbs(is_active);

-- 7. 药材库存表 (herb_inventory)
CREATE TABLE herb_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    herb_id UUID NOT NULL,
    batch_number VARCHAR(50),
    supplier VARCHAR(100),
    purchase_date DATE,
    expiry_date DATE,
    quantity DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    unit_price DECIMAL(10,2),
    quality_grade VARCHAR(20),
    storage_location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'low_stock', 'out_of_stock', 'expired')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE herb_inventory IS '药材库存表';
COMMENT ON COLUMN herb_inventory.herb_id IS '药材ID';
COMMENT ON COLUMN herb_inventory.batch_number IS '批次号';
COMMENT ON COLUMN herb_inventory.supplier IS '供应商';
COMMENT ON COLUMN herb_inventory.purchase_date IS '采购日期';
COMMENT ON COLUMN herb_inventory.expiry_date IS '过期日期';
COMMENT ON COLUMN herb_inventory.quantity IS '库存数量';
COMMENT ON COLUMN herb_inventory.unit IS '单位（克、千克等）';
COMMENT ON COLUMN herb_inventory.unit_price IS '单价';
COMMENT ON COLUMN herb_inventory.quality_grade IS '质量等级';
COMMENT ON COLUMN herb_inventory.storage_location IS '存储位置';
COMMENT ON COLUMN herb_inventory.status IS '库存状态';
COMMENT ON COLUMN herb_inventory.created_at IS '创建时间';
COMMENT ON COLUMN herb_inventory.updated_at IS '更新时间';

-- 为 herb_inventory 表创建更新时间触发器
CREATE TRIGGER update_herb_inventory_updated_at BEFORE UPDATE ON herb_inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加外键约束
ALTER TABLE herb_inventory ADD CONSTRAINT fk_herb_inventory_herb_id FOREIGN KEY (herb_id) REFERENCES herbs(id) ON DELETE CASCADE;

-- 为 herb_inventory 表创建索引
CREATE INDEX idx_herb_inventory_herb_id ON herb_inventory(herb_id);
CREATE INDEX idx_herb_inventory_batch_number ON herb_inventory(batch_number);
CREATE INDEX idx_herb_inventory_status ON herb_inventory(status);
CREATE INDEX idx_herb_inventory_expiry_date ON herb_inventory(expiry_date);

-- 8. 方剂表 (prescriptions) - 中医方剂库
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    source VARCHAR(100), -- 出处（如：《伤寒论》、《金匮要略》等）
    category VARCHAR(50),
    composition TEXT NOT NULL, -- JSON格式：药材名称和用量
    preparation_method TEXT,
    usage_dosage TEXT,
    indication TEXT,
    syndrome_adaptation TEXT,
    contraindications TEXT,
    modifications TEXT, -- 加减变化
    clinical_notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE prescriptions IS '方剂表';
COMMENT ON COLUMN prescriptions.name IS '方剂名称';
COMMENT ON COLUMN prescriptions.source IS '出处（如：《伤寒论》、《金匮要略》等）';
COMMENT ON COLUMN prescriptions.category IS '方剂分类';
COMMENT ON COLUMN prescriptions.composition IS '组成（JSON格式：药材名称和用量）';
COMMENT ON COLUMN prescriptions.preparation_method IS '制法';
COMMENT ON COLUMN prescriptions.usage_dosage IS '用法用量';
COMMENT ON COLUMN prescriptions.indication IS '主治';
COMMENT ON COLUMN prescriptions.syndrome_adaptation IS '证候适应';
COMMENT ON COLUMN prescriptions.contraindications IS '禁忌';
COMMENT ON COLUMN prescriptions.modifications IS '加减变化';
COMMENT ON COLUMN prescriptions.clinical_notes IS '临床运用';
COMMENT ON COLUMN prescriptions.is_active IS '是否启用';
COMMENT ON COLUMN prescriptions.created_at IS '创建时间';
COMMENT ON COLUMN prescriptions.updated_at IS '更新时间';

-- 为 prescriptions 表创建更新时间触发器
CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 prescriptions 表创建索引
CREATE INDEX idx_prescriptions_name ON prescriptions(name);
CREATE INDEX idx_prescriptions_source ON prescriptions(source);
CREATE INDEX idx_prescriptions_category ON prescriptions(category);
CREATE INDEX idx_prescriptions_is_active ON prescriptions(is_active);

-- 9. 对话记录表 (conversations)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_id VARCHAR(50) NOT NULL,
    conversation_type VARCHAR(30) NOT NULL CHECK (conversation_type IN ('diagnosis', 'herb_consultation', 'classic_search', 'case_reference', 'image_analysis', 'general_chat')),
    title VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    total_messages INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE conversations IS '对话记录表';
COMMENT ON COLUMN conversations.user_id IS '用户ID';
COMMENT ON COLUMN conversations.session_id IS '会话ID';
COMMENT ON COLUMN conversations.conversation_type IS '对话类型';
COMMENT ON COLUMN conversations.title IS '对话标题';
COMMENT ON COLUMN conversations.status IS '对话状态';
COMMENT ON COLUMN conversations.total_messages IS '消息总数';
COMMENT ON COLUMN conversations.created_at IS '创建时间';
COMMENT ON COLUMN conversations.updated_at IS '更新时间';

-- 为 conversations 表创建更新时间触发器
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加外键约束
ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 为 conversations 表创建索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_conversation_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- 10. 消息表 (messages)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'prescription', 'diagnosis')),
    metadata JSONB, -- PostgreSQL JSONB类型
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE messages IS '消息表';
COMMENT ON COLUMN messages.conversation_id IS '对话ID';
COMMENT ON COLUMN messages.role IS '消息角色';
COMMENT ON COLUMN messages.content IS '消息内容';
COMMENT ON COLUMN messages.message_type IS '消息类型';
COMMENT ON COLUMN messages.metadata IS '元数据（JSON格式）';
COMMENT ON COLUMN messages.is_deleted IS '是否删除';
COMMENT ON COLUMN messages.created_at IS '创建时间';

-- 添加外键约束
ALTER TABLE messages ADD CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

-- 为 messages 表创建索引
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_message_type ON messages(message_type);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);

-- 11. 舌苔分析记录表 (tongue_analysis)
CREATE TABLE tongue_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    analysis_result JSONB NOT NULL, -- PostgreSQL JSONB类型
    color_analysis VARCHAR(100),
    coating_thickness VARCHAR(50),
    coating_moisture VARCHAR(50),
    coating_color VARCHAR(50),
    tongue_shape VARCHAR(50),
    syndrome_suggestion TEXT,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tongue_analysis IS '舌苔分析记录表';
COMMENT ON COLUMN tongue_analysis.user_id IS '用户ID';
COMMENT ON COLUMN tongue_analysis.image_url IS '舌苔图片URL';
COMMENT ON COLUMN tongue_analysis.analysis_result IS '分析结果（JSON格式）';
COMMENT ON COLUMN tongue_analysis.color_analysis IS '颜色分析';
COMMENT ON COLUMN tongue_analysis.coating_thickness IS '苔质厚薄';
COMMENT ON COLUMN tongue_analysis.coating_moisture IS '苔质润燥';
COMMENT ON COLUMN tongue_analysis.coating_color IS '苔色';
COMMENT ON COLUMN tongue_analysis.tongue_shape IS '舌形';
COMMENT ON COLUMN tongue_analysis.syndrome_suggestion IS '证型建议';
COMMENT ON COLUMN tongue_analysis.confidence_score IS '置信度';
COMMENT ON COLUMN tongue_analysis.created_at IS '创建时间';

-- 添加外键约束
ALTER TABLE tongue_analysis ADD CONSTRAINT fk_tongue_analysis_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 为 tongue_analysis 表创建索引
CREATE INDEX idx_tongue_analysis_user_id ON tongue_analysis(user_id);
CREATE INDEX idx_tongue_analysis_created_at ON tongue_analysis(created_at);
CREATE INDEX idx_tongue_analysis_user_created ON tongue_analysis(user_id, created_at);

-- 12. 方剂推荐记录表 (prescription_recommendations)
CREATE TABLE prescription_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID,
    user_id UUID NOT NULL,
    prescription_id UUID,
    prescription_name VARCHAR(100) NOT NULL,
    syndrome_type VARCHAR(100),
    recommendation_reason TEXT,
    dosage_instruction TEXT,
    precautions TEXT,
    confidence_score DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'recommended' CHECK (status IN ('recommended', 'accepted', 'rejected', 'modified')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE prescription_recommendations IS '方剂推荐记录表';
COMMENT ON COLUMN prescription_recommendations.case_id IS '关联病例ID';
COMMENT ON COLUMN prescription_recommendations.user_id IS '用户ID';
COMMENT ON COLUMN prescription_recommendations.prescription_id IS '推荐方剂ID';
COMMENT ON COLUMN prescription_recommendations.prescription_name IS '方剂名称';
COMMENT ON COLUMN prescription_recommendations.syndrome_type IS '对应证型';
COMMENT ON COLUMN prescription_recommendations.recommendation_reason IS '推荐理由';
COMMENT ON COLUMN prescription_recommendations.dosage_instruction IS '用法用量';
COMMENT ON COLUMN prescription_recommendations.precautions IS '注意事项';
COMMENT ON COLUMN prescription_recommendations.confidence_score IS '推荐置信度';
COMMENT ON COLUMN prescription_recommendations.status IS '推荐状态';
COMMENT ON COLUMN prescription_recommendations.created_at IS '创建时间';
COMMENT ON COLUMN prescription_recommendations.updated_at IS '更新时间';

-- 为 prescription_recommendations 表创建更新时间触发器
CREATE TRIGGER update_prescription_recommendations_updated_at BEFORE UPDATE ON prescription_recommendations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加外键约束
ALTER TABLE prescription_recommendations ADD CONSTRAINT fk_prescription_recommendations_case_id FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE SET NULL;
ALTER TABLE prescription_recommendations ADD CONSTRAINT fk_prescription_recommendations_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE prescription_recommendations ADD CONSTRAINT fk_prescription_recommendations_prescription_id FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE SET NULL;

-- 为 prescription_recommendations 表创建索引
CREATE INDEX idx_prescription_recommendations_case_id ON prescription_recommendations(case_id);
CREATE INDEX idx_prescription_recommendations_user_id ON prescription_recommendations(user_id);
CREATE INDEX idx_prescription_recommendations_prescription_id ON prescription_recommendations(prescription_id);
CREATE INDEX idx_prescription_recommendations_status ON prescription_recommendations(status);
CREATE INDEX idx_prescription_recommendations_created_at ON prescription_recommendations(created_at);
CREATE INDEX idx_prescription_recommendations_user_created ON prescription_recommendations(user_id, created_at);

-- 13. 古籍条文表 (classic_texts) - 中医经典文献
CREATE TABLE classic_texts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(100) NOT NULL,
    chapter VARCHAR(100),
    section VARCHAR(100),
    article_number VARCHAR(20),
    content TEXT NOT NULL,
    translation TEXT,
    annotation TEXT,
    clinical_application TEXT,
    related_syndromes TEXT, -- JSON格式
    related_prescriptions TEXT, -- JSON格式
    source_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE classic_texts IS '古籍条文表';
COMMENT ON COLUMN classic_texts.title IS '古籍名称';
COMMENT ON COLUMN classic_texts.chapter IS '章节';
COMMENT ON COLUMN classic_texts.section IS '节';
COMMENT ON COLUMN classic_texts.article_number IS '条文编号';
COMMENT ON COLUMN classic_texts.content IS '条文内容';
COMMENT ON COLUMN classic_texts.translation IS '现代译文';
COMMENT ON COLUMN classic_texts.annotation IS '注释';
COMMENT ON COLUMN classic_texts.clinical_application IS '临床应用';
COMMENT ON COLUMN classic_texts.related_syndromes IS '相关证型（JSON格式）';
COMMENT ON COLUMN classic_texts.related_prescriptions IS '相关方剂（JSON格式）';
COMMENT ON COLUMN classic_texts.source_url IS '来源链接';
COMMENT ON COLUMN classic_texts.is_active IS '是否启用';
COMMENT ON COLUMN classic_texts.created_at IS '创建时间';
COMMENT ON COLUMN classic_texts.updated_at IS '更新时间';

-- 为 classic_texts 表创建更新时间触发器
CREATE TRIGGER update_classic_texts_updated_at BEFORE UPDATE ON classic_texts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 classic_texts 表创建索引
CREATE INDEX idx_classic_texts_title ON classic_texts(title);
CREATE INDEX idx_classic_texts_chapter ON classic_texts(chapter);
CREATE INDEX idx_classic_texts_article_number ON classic_texts(article_number);
CREATE INDEX idx_classic_texts_is_active ON classic_texts(is_active);

-- 为 classic_texts 表创建全文搜索索引
CREATE INDEX idx_classic_texts_content_gin ON classic_texts USING gin(to_tsvector('english', COALESCE(content,'') || ' ' || COALESCE(translation,'') || ' ' || COALESCE(annotation,'')));

-- 14. 医案表 (medical_records) - 临床医案库
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_title VARCHAR(200) NOT NULL,
    patient_age INTEGER,
    patient_gender VARCHAR(10) CHECK (patient_gender IN ('male', 'female', 'other')),
    chief_complaint TEXT NOT NULL,
    present_illness TEXT NOT NULL,
    symptoms TEXT NOT NULL, -- JSON格式
    tongue_pulse TEXT,
    syndrome_diagnosis VARCHAR(100) NOT NULL,
    treatment_principle TEXT,
    prescription TEXT NOT NULL,
    dosage_instruction TEXT,
    treatment_course TEXT,
    outcome TEXT,
    doctor_name VARCHAR(50),
    hospital_name VARCHAR(100),
    case_source VARCHAR(100),
    tags TEXT, -- JSON格式
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE medical_records IS '医案表';
COMMENT ON COLUMN medical_records.case_title IS '医案标题';
COMMENT ON COLUMN medical_records.patient_age IS '患者年龄';
COMMENT ON COLUMN medical_records.patient_gender IS '患者性别';
COMMENT ON COLUMN medical_records.chief_complaint IS '主诉';
COMMENT ON COLUMN medical_records.present_illness IS '现病史';
COMMENT ON COLUMN medical_records.symptoms IS '症状（JSON格式）';
COMMENT ON COLUMN medical_records.tongue_pulse IS '舌脉';
COMMENT ON COLUMN medical_records.syndrome_diagnosis IS '证型诊断';
COMMENT ON COLUMN medical_records.treatment_principle IS '治则治法';
COMMENT ON COLUMN medical_records.prescription IS '方药';
COMMENT ON COLUMN medical_records.dosage_instruction IS '用法用量';
COMMENT ON COLUMN medical_records.treatment_course IS '治疗经过';
COMMENT ON COLUMN medical_records.outcome IS '治疗结果';
COMMENT ON COLUMN medical_records.doctor_name IS '医生姓名';
COMMENT ON COLUMN medical_records.hospital_name IS '医院名称';
COMMENT ON COLUMN medical_records.case_source IS '医案来源';
COMMENT ON COLUMN medical_records.tags IS '标签（JSON格式）';
COMMENT ON COLUMN medical_records.is_active IS '是否启用';
COMMENT ON COLUMN medical_records.created_at IS '创建时间';
COMMENT ON COLUMN medical_records.updated_at IS '更新时间';

-- 为 medical_records 表创建更新时间触发器
CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 medical_records 表创建索引
CREATE INDEX idx_medical_records_syndrome_diagnosis ON medical_records(syndrome_diagnosis);
CREATE INDEX idx_medical_records_doctor_name ON medical_records(doctor_name);
CREATE INDEX idx_medical_records_hospital_name ON medical_records(hospital_name);
CREATE INDEX idx_medical_records_is_active ON medical_records(is_active);

-- 为 medical_records 表创建全文搜索索引
CREATE INDEX idx_medical_records_content_gin ON medical_records USING gin(to_tsvector('english', COALESCE(chief_complaint,'') || ' ' || COALESCE(present_illness,'') || ' ' || COALESCE(symptoms,'') || ' ' || COALESCE(treatment_principle,'') || ' ' || COALESCE(prescription,'')));

-- 15. 系统配置表 (system_configs)
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'string' CHECK (config_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE system_configs IS '系统配置表';
COMMENT ON COLUMN system_configs.config_key IS '配置键';
COMMENT ON COLUMN system_configs.config_value IS '配置值';
COMMENT ON COLUMN system_configs.config_type IS '配置类型';
COMMENT ON COLUMN system_configs.description IS '配置描述';
COMMENT ON COLUMN system_configs.is_active IS '是否启用';
COMMENT ON COLUMN system_configs.created_at IS '创建时间';
COMMENT ON COLUMN system_configs.updated_at IS '更新时间';

-- 为 system_configs 表创建更新时间触发器
CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 为 system_configs 表创建索引
CREATE INDEX idx_system_configs_config_key ON system_configs(config_key);
CREATE INDEX idx_system_configs_is_active ON system_configs(is_active);

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description) VALUES
('tcm_model_provider', 'DEEPSEEK_TCM', 'string', '中医模型提供商'),
('max_conversation_length', '100', 'number', '最大对话长度'),
('enable_tongue_analysis', 'true', 'boolean', '是否启用舌苔分析'),
('enable_prescription_check', 'true', 'boolean', '是否启用方剂配伍检查'),
('cache_ttl', '3600', 'number', '缓存过期时间（秒）'),
('max_file_size', '10485760', 'number', '最大文件大小（字节）'),
('supported_image_formats', '["jpg", "jpeg", "png", "bmp"]', 'json', '支持的图片格式');

-- 16. 用户状态表 (user_states)
CREATE TABLE user_states (
    app_name varchar(128) NOT NULL,
    user_id  UUID DEFAULT uuid_generate_v4(),
    state jsonb NOT NULL,
    update_time timestamp(6) NOT NULL,
    CONSTRAINT user_states_pkey PRIMARY KEY (app_name, user_id)
);
COMMENT ON TABLE user_states IS '用户状态表';
COMMENT ON COLUMN user_states.app_name IS '应用名称';
COMMENT ON COLUMN user_states.user_id IS '用户ID';
COMMENT ON COLUMN user_states.state IS '状态数据';
COMMENT ON COLUMN user_states.update_time IS '更新时间';

-- 为 user_states 表创建索引
CREATE INDEX idx_user_states_app_name ON user_states USING btree (app_name);
CREATE INDEX idx_user_states_app_name_user_id ON user_states USING btree (app_name, user_id);
CREATE INDEX idx_user_states_app_user ON user_states USING btree (app_name, user_id);
CREATE INDEX idx_user_states_update_time ON user_states USING btree (update_time);
CREATE INDEX idx_user_states_user_id ON user_states USING btree (user_id);

-- 17. 用户会话表 (user_sessions)
CREATE TABLE user_sessions (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    session_token varchar(255) NOT NULL,
    access_token varchar(500) NULL,
    refresh_token varchar(500) NULL,
    device_id varchar(255) NULL,
    device_type varchar(50) NULL,
    user_agent text NULL,
    ip_address inet NULL,
    "location" jsonb NULL,
    expires_at timestamptz(6) NOT NULL,
    last_activity_at timestamptz(6) DEFAULT now() NULL,
    created_at timestamptz(6) DEFAULT now() NULL,
    is_active bool DEFAULT true NULL,
    CONSTRAINT user_sessions_pkey PRIMARY KEY (id),
    CONSTRAINT user_sessions_session_token_key UNIQUE (session_token),
    CONSTRAINT valid_device_type CHECK (((device_type)::text = ANY (ARRAY[('web'::character varying)::text, ('mobile'::character varying)::text, ('desktop'::character varying)::text, ('unknown'::character varying)::text]))
);
COMMENT ON TABLE user_sessions IS '用户会话表';
COMMENT ON COLUMN user_sessions.id IS '会话ID';
COMMENT ON COLUMN user_sessions.user_id IS '用户ID';
COMMENT ON COLUMN user_sessions.session_token IS '会话令牌';
COMMENT ON COLUMN user_sessions.access_token IS '访问令牌';
COMMENT ON COLUMN user_sessions.refresh_token IS '刷新令牌';
COMMENT ON COLUMN user_sessions.device_id IS '设备ID';
COMMENT ON COLUMN user_sessions.device_type IS '设备类型';
COMMENT ON COLUMN user_sessions.user_agent IS '用户代理';
COMMENT ON COLUMN user_sessions.ip_address IS 'IP地址';
COMMENT ON COLUMN user_sessions."location" IS '位置信息';
COMMENT ON COLUMN user_sessions.expires_at IS '过期时间';
COMMENT ON COLUMN user_sessions.last_activity_at IS '最后活动时间';
COMMENT ON COLUMN user_sessions.created_at IS '创建时间';
COMMENT ON COLUMN user_sessions.is_active IS '是否激活';

-- 为 user_sessions 表创建索引
CREATE INDEX idx_sessions_active ON user_sessions USING btree (is_active);
CREATE INDEX idx_sessions_device_id ON user_sessions USING btree (device_id);
CREATE INDEX idx_sessions_expires_at ON user_sessions USING btree (expires_at);
CREATE INDEX idx_sessions_token ON user_sessions USING btree (session_token);
CREATE INDEX idx_sessions_user_id ON user_sessions USING btree (user_id);

-- 添加外键约束
ALTER TABLE user_sessions ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 18. 用户活动表 (user_activities)
CREATE TABLE user_activities (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    session_id uuid NULL,
    activity_type varchar(50) NOT NULL,
    activity_data jsonb DEFAULT '{}'::jsonb NULL,
    ip_address varchar(50) NULL,
    user_agent text NULL,
    resource varchar(255) NULL,
    created_at timestamptz(6) DEFAULT now() NULL,
    CONSTRAINT user_activities_pkey PRIMARY KEY (id),
    CONSTRAINT valid_activity_type CHECK (((activity_type)::text = ANY (ARRAY[('login'::character varying)::text, ('logout'::character varying)::text, ('register'::character varying)::text, ('password_change'::character varying)::text, ('email_verify'::character varying)::text, ('profile_update'::character varying)::text, ('session_expire'::character varying)::text]))
);
COMMENT ON TABLE user_activities IS '用户活动表';
COMMENT ON COLUMN user_activities.id IS '活动ID';
COMMENT ON COLUMN user_activities.user_id IS '用户ID';
COMMENT ON COLUMN user_activities.session_id IS '会话ID';
COMMENT ON COLUMN user_activities.activity_type IS '活动类型';
COMMENT ON COLUMN user_activities.activity_data IS '活动数据';
COMMENT ON COLUMN user_activities.ip_address IS 'IP地址';
COMMENT ON COLUMN user_activities.user_agent IS '用户代理';
COMMENT ON COLUMN user_activities.resource IS '资源';
COMMENT ON COLUMN user_activities.created_at IS '创建时间';

-- 为 user_activities 表创建索引
CREATE INDEX idx_activities_created_at ON user_activities USING btree (created_at);
CREATE INDEX idx_activities_type ON user_activities USING btree (activity_type);
CREATE INDEX idx_activities_user_id ON user_activities USING btree (user_id);

-- 添加外键约束
ALTER TABLE user_activities ADD CONSTRAINT user_activities_session_id_fkey FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE SET NULL;
ALTER TABLE user_activities ADD CONSTRAINT user_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 19. 刷新令牌表 (refresh_tokens)
CREATE TABLE refresh_tokens (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    token_hash varchar(255) NOT NULL,
    session_id uuid NULL,
    expires_at timestamptz(6) NOT NULL,
    created_at timestamptz(6) DEFAULT now() NULL,
    revoked_at timestamptz(6) NULL,
    is_revoked bool DEFAULT false NULL,
    CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id),
    CONSTRAINT refresh_tokens_token_hash_key UNIQUE (token_hash)
);
COMMENT ON TABLE refresh_tokens IS '刷新令牌表';
COMMENT ON COLUMN refresh_tokens.id IS '主键ID';
COMMENT ON COLUMN refresh_tokens.user_id IS '用户ID';
COMMENT ON COLUMN refresh_tokens.token_hash IS '令牌哈希值';
COMMENT ON COLUMN refresh_tokens.session_id IS '会话ID';
COMMENT ON COLUMN refresh_tokens.expires_at IS '过期时间';
COMMENT ON COLUMN refresh_tokens.created_at IS '创建时间';
COMMENT ON COLUMN refresh_tokens.revoked_at IS '撤销时间';
COMMENT ON COLUMN refresh_tokens.is_revoked IS '是否已撤销';

-- 为 refresh_tokens 表创建索引
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens USING btree (expires_at);
CREATE INDEX idx_refresh_tokens_revoked ON refresh_tokens USING btree (is_revoked);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens USING btree (token_hash);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens USING btree (user_id);

-- 添加外键约束
ALTER TABLE refresh_tokens ADD CONSTRAINT refresh_tokens_session_id_fkey FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE CASCADE;
ALTER TABLE refresh_tokens ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 创建视图：患者完整信息视图
CREATE VIEW patient_full_info AS
SELECT
    u.id as user_id,
    u.username,
    u.email,
    u.real_name,
    u.phone,
    u.gender,
    u.birth_date,
    u.constitution_type,
    p.patient_code,
    p.medical_history,
    p.family_history,
    p.allergy_info,
    p.current_medications,
    p.emergency_contact_name,
    p.emergency_contact_phone,
    u.created_at as registration_date
FROM users u
LEFT JOIN patients p ON u.id = p.user_id
WHERE u.role = 'patient';

-- 创建视图：病例统计视图
CREATE VIEW case_statistics AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_cases,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_cases,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_cases,
    AVG(syndrome_confidence) as avg_confidence
FROM medical_cases
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 创建函数：获取患者最近病例
CREATE OR REPLACE FUNCTION GetPatientRecentCases(patient_id_param UUID, limit_count_param INTEGER)
RETURNS TABLE(
    id UUID,
    patient_id UUID,
    case_code VARCHAR(20),
    chief_complaint TEXT,
    present_illness TEXT,
    symptoms TEXT,
    tongue_description TEXT,
    pulse_description TEXT,
    syndrome_type VARCHAR(100),
    syndrome_confidence DECIMAL(3,2),
    treatment_principle TEXT,
    prescription_name VARCHAR(100),
    prescription_ingredients TEXT,
    dosage_instruction TEXT,
    precautions TEXT,
    follow_up_date DATE,
    status VARCHAR(20),
    doctor_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    syndrome_name VARCHAR(100),
    syndrome_description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mc.id,
        mc.patient_id,
        mc.case_code,
        mc.chief_complaint,
        mc.present_illness,
        mc.symptoms,
        mc.tongue_description,
        mc.pulse_description,
        mc.syndrome_type,
        mc.syndrome_confidence,
        mc.treatment_principle,
        mc.prescription_name,
        mc.prescription_ingredients,
        mc.dosage_instruction,
        mc.precautions,
        mc.follow_up_date,
        mc.status,
        mc.doctor_notes,
        mc.created_at,
        mc.updated_at,
        s.name as syndrome_name,
        s.description as syndrome_description
    FROM medical_cases mc
    LEFT JOIN syndromes s ON mc.syndrome_type = s.name
    WHERE mc.patient_id = patient_id_param
    ORDER BY mc.created_at DESC
    LIMIT limit_count_param;
END;
$$ LANGUAGE plpgsql;

-- 创建函数：更新药材库存
CREATE OR REPLACE FUNCTION UpdateHerbInventory(
    herb_id_param UUID,
    quantity_change_param DECIMAL(10,3),
    operation_type_param VARCHAR(10) -- 'add' or 'subtract'
)
RETURNS VOID AS $$
DECLARE
    current_quantity DECIMAL(10,3);
BEGIN
    SELECT quantity INTO current_quantity
    FROM herb_inventory
    WHERE herb_id = herb_id_param AND status = 'available'
    ORDER BY created_at DESC
    LIMIT 1;

    IF operation_type_param = 'add' THEN
        UPDATE herb_inventory
        SET quantity = quantity + quantity_change_param,
            updated_at = CURRENT_TIMESTAMP
        WHERE herb_id = herb_id_param AND status = 'available'
        ORDER BY created_at DESC
        LIMIT 1;
    ELSE
        UPDATE herb_inventory
        SET quantity = GREATEST(0, quantity - quantity_change_param),
            status = CASE
                WHEN quantity - quantity_change_param <= 0 THEN 'out_of_stock'
                WHEN quantity - quantity_change_param <= 10 THEN 'low_stock'
                ELSE 'available'
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE herb_id = herb_id_param AND status = 'available'
        ORDER BY created_at DESC
        LIMIT 1;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器：自动更新对话消息计数
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET total_messages = total_messages + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversation_message_count_trigger
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_message_count();

-- 创建触发器：自动更新病例状态
CREATE OR REPLACE FUNCTION update_case_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.follow_up_date IS NOT NULL AND NEW.follow_up_date <= CURRENT_DATE THEN
        NEW.status = 'completed';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_case_status_trigger
BEFORE UPDATE ON medical_cases
FOR EACH ROW
EXECUTE FUNCTION update_case_status();

-- 为 herbs 表创建全文搜索索引
CREATE INDEX idx_herbs_content_gin ON herbs USING gin(to_tsvector('english', COALESCE(name,'') || ' ' || COALESCE(effect,'') || ' ' || COALESCE(indication,'')));

-- 完成数据库初始化
SELECT 'SmartTCM-Agent PostgreSQL 数据库初始化完成！' as message;