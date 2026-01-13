-- SmartTCM-Agent 中医问诊系统数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS tcm_agent_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tcm_agent_db;

-- 1. 用户表 (users)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('patient', 'doctor', 'admin') DEFAULT 'patient' COMMENT '用户角色',
    real_name VARCHAR(50) COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号',
    gender ENUM('male', 'female', 'other') COMMENT '性别',
    birth_date DATE COMMENT '出生日期',
    constitution_type VARCHAR(50) COMMENT '体质类型（如：阳虚质、阴虚质等）',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB COMMENT='用户表';

-- 2. 患者表 (patients) - 扩展用户信息
CREATE TABLE patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '关联用户ID',
    patient_code VARCHAR(20) UNIQUE NOT NULL COMMENT '患者编号',
    medical_history TEXT COMMENT '既往病史',
    family_history TEXT COMMENT '家族病史',
    allergy_info TEXT COMMENT '过敏信息',
    current_medications TEXT COMMENT '当前用药情况',
    emergency_contact_name VARCHAR(50) COMMENT '紧急联系人姓名',
    emergency_contact_phone VARCHAR(20) COMMENT '紧急联系人电话',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_code (patient_code),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB COMMENT='患者详细信息表';

-- 3. 病例表 (medical_cases)
CREATE TABLE medical_cases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL COMMENT '患者ID',
    case_code VARCHAR(20) UNIQUE NOT NULL COMMENT '病例编号',
    chief_complaint TEXT NOT NULL COMMENT '主诉',
    present_illness TEXT COMMENT '现病史',
    symptoms TEXT NOT NULL COMMENT '症状描述（JSON格式存储）',
    tongue_description TEXT COMMENT '舌象描述',
    pulse_description TEXT COMMENT '脉象描述',
    syndrome_type VARCHAR(100) COMMENT '辨证结果（证型）',
    syndrome_confidence DECIMAL(3,2) COMMENT '辨证置信度（0-1）',
    treatment_principle TEXT COMMENT '治则治法',
    prescription_name VARCHAR(100) COMMENT '推荐方剂名称',
    prescription_ingredients TEXT COMMENT '方剂组成（JSON格式）',
    dosage_instruction TEXT COMMENT '用法用量',
    precautions TEXT COMMENT '注意事项',
    follow_up_date DATE COMMENT '复诊日期',
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active' COMMENT '病例状态',
    doctor_notes TEXT COMMENT '医生备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_case_code (case_code),
    INDEX idx_syndrome_type (syndrome_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='病例表';

-- 4. 症状表 (symptoms) - 标准化症状库
CREATE TABLE symptoms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '症状名称',
    category VARCHAR(50) NOT NULL COMMENT '症状分类（如：寒热、汗出、二便等）',
    description TEXT COMMENT '症状描述',
    severity_levels TEXT COMMENT '严重程度分级（JSON格式）',
    related_syndromes TEXT COMMENT '相关证型（JSON格式）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='症状库表';

-- 5. 证型表 (syndromes) - 中医证型库
CREATE TABLE syndromes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '证型名称',
    category VARCHAR(50) NOT NULL COMMENT '证型分类（如：八纲辨证、脏腑辨证等）',
    description TEXT COMMENT '证型描述',
    main_symptoms TEXT COMMENT '主要症状（JSON格式）',
    treatment_principle TEXT COMMENT '治则治法',
    common_prescriptions TEXT COMMENT '常用方剂（JSON格式）',
    precautions TEXT COMMENT '注意事项',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='证型库表';

-- 6. 药材表 (herbs) - 中药材基础信息
CREATE TABLE herbs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '药材名称',
    pinyin VARCHAR(100) COMMENT '拼音',
    latin_name VARCHAR(100) COMMENT '拉丁学名',
    category VARCHAR(50) COMMENT '药材分类（如：补虚药、清热药等）',
    nature VARCHAR(20) COMMENT '药性（寒、热、温、凉、平）',
    flavor VARCHAR(50) COMMENT '五味（辛、甘、酸、苦、咸）',
    meridian VARCHAR(100) COMMENT '归经',
    effect TEXT COMMENT '功效',
    indication TEXT COMMENT '主治',
    usage_dosage TEXT COMMENT '用法用量',
    contraindications TEXT COMMENT '禁忌',
    incompatibilities TEXT COMMENT '配伍禁忌（十八反、十九畏等）',
    processing_method TEXT COMMENT '炮制方法',
    storage_method TEXT COMMENT '贮藏方法',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_nature (nature),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='药材表';

-- 7. 药材库存表 (herb_inventory)
CREATE TABLE herb_inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    herb_id INT NOT NULL COMMENT '药材ID',
    batch_number VARCHAR(50) COMMENT '批次号',
    supplier VARCHAR(100) COMMENT '供应商',
    purchase_date DATE COMMENT '采购日期',
    expiry_date DATE COMMENT '过期日期',
    quantity DECIMAL(10,3) NOT NULL COMMENT '库存数量',
    unit VARCHAR(20) NOT NULL COMMENT '单位（克、千克等）',
    unit_price DECIMAL(10,2) COMMENT '单价',
    quality_grade VARCHAR(20) COMMENT '质量等级',
    storage_location VARCHAR(100) COMMENT '存储位置',
    status ENUM('available', 'low_stock', 'out_of_stock', 'expired') DEFAULT 'available' COMMENT '库存状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (herb_id) REFERENCES herbs(id) ON DELETE CASCADE,
    INDEX idx_herb_id (herb_id),
    INDEX idx_batch_number (batch_number),
    INDEX idx_status (status),
    INDEX idx_expiry_date (expiry_date)
) ENGINE=InnoDB COMMENT='药材库存表';

-- 8. 方剂表 (prescriptions) - 中医方剂库
CREATE TABLE prescriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '方剂名称',
    source VARCHAR(100) COMMENT '出处（如：《伤寒论》、《金匮要略》等）',
    category VARCHAR(50) COMMENT '方剂分类',
    composition TEXT NOT NULL COMMENT '组成（JSON格式：药材名称和用量）',
    preparation_method TEXT COMMENT '制法',
    usage_dosage TEXT COMMENT '用法用量',
    indication TEXT COMMENT '主治',
    syndrome_adaptation TEXT COMMENT '证候适应',
    contraindications TEXT COMMENT '禁忌',
    modifications TEXT COMMENT '加减变化',
    clinical_notes TEXT COMMENT '临床运用',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_source (source),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='方剂表';

-- 9. 对话记录表 (conversations)
CREATE TABLE conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    session_id VARCHAR(50) NOT NULL COMMENT '会话ID',
    conversation_type ENUM('diagnosis', 'herb_consultation', 'classic_search', 'case_reference', 'image_analysis', 'general_chat') NOT NULL COMMENT '对话类型',
    title VARCHAR(200) COMMENT '对话标题',
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active' COMMENT '对话状态',
    total_messages INT DEFAULT 0 COMMENT '消息总数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_conversation_type (conversation_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='对话记录表';

-- 10. 消息表 (messages)
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL COMMENT '对话ID',
    role ENUM('user', 'assistant', 'system') NOT NULL COMMENT '消息角色',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type ENUM('text', 'image', 'file', 'prescription', 'diagnosis') DEFAULT 'text' COMMENT '消息类型',
    metadata JSON COMMENT '元数据（JSON格式）',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_role (role),
    INDEX idx_message_type (message_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='消息表';

-- 11. 舌苔分析记录表 (tongue_analysis)
CREATE TABLE tongue_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    image_url VARCHAR(255) NOT NULL COMMENT '舌苔图片URL',
    analysis_result JSON NOT NULL COMMENT '分析结果（JSON格式）',
    color_analysis VARCHAR(100) COMMENT '颜色分析',
    coating_thickness VARCHAR(50) COMMENT '苔质厚薄',
    coating_moisture VARCHAR(50) COMMENT '苔质润燥',
    coating_color VARCHAR(50) COMMENT '苔色',
    tongue_shape VARCHAR(50) COMMENT '舌形',
    syndrome_suggestion TEXT COMMENT '证型建议',
    confidence_score DECIMAL(3,2) COMMENT '置信度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='舌苔分析记录表';

-- 12. 方剂推荐记录表 (prescription_recommendations)
CREATE TABLE prescription_recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    case_id INT COMMENT '关联病例ID',
    user_id INT NOT NULL COMMENT '用户ID',
    prescription_id INT COMMENT '推荐方剂ID',
    prescription_name VARCHAR(100) NOT NULL COMMENT '方剂名称',
    syndrome_type VARCHAR(100) COMMENT '对应证型',
    recommendation_reason TEXT COMMENT '推荐理由',
    dosage_instruction TEXT COMMENT '用法用量',
    precautions TEXT COMMENT '注意事项',
    confidence_score DECIMAL(3,2) COMMENT '推荐置信度',
    status ENUM('recommended', 'accepted', 'rejected', 'modified') DEFAULT 'recommended' COMMENT '推荐状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE SET NULL,
    INDEX idx_case_id (case_id),
    INDEX idx_user_id (user_id),
    INDEX idx_prescription_id (prescription_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='方剂推荐记录表';

-- 13. 古籍条文表 (classic_texts) - 中医经典文献
CREATE TABLE classic_texts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL COMMENT '古籍名称',
    chapter VARCHAR(100) COMMENT '章节',
    section VARCHAR(100) COMMENT '节',
    article_number VARCHAR(20) COMMENT '条文编号',
    content TEXT NOT NULL COMMENT '条文内容',
    translation TEXT COMMENT '现代译文',
    annotation TEXT COMMENT '注释',
    clinical_application TEXT COMMENT '临床应用',
    related_syndromes TEXT COMMENT '相关证型（JSON格式）',
    related_prescriptions TEXT COMMENT '相关方剂（JSON格式）',
    source_url VARCHAR(255) COMMENT '来源链接',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_title (title),
    INDEX idx_chapter (chapter),
    INDEX idx_article_number (article_number),
    INDEX idx_is_active (is_active),
    FULLTEXT idx_content (content, translation, annotation)
) ENGINE=InnoDB COMMENT='古籍条文表';

-- 14. 医案表 (medical_records) - 临床医案库
CREATE TABLE medical_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    case_title VARCHAR(200) NOT NULL COMMENT '医案标题',
    patient_age INT COMMENT '患者年龄',
    patient_gender ENUM('male', 'female', 'other') COMMENT '患者性别',
    chief_complaint TEXT NOT NULL COMMENT '主诉',
    present_illness TEXT NOT NULL COMMENT '现病史',
    symptoms TEXT NOT NULL COMMENT '症状（JSON格式）',
    tongue_pulse TEXT COMMENT '舌脉',
    syndrome_diagnosis VARCHAR(100) NOT NULL COMMENT '证型诊断',
    treatment_principle TEXT COMMENT '治则治法',
    prescription TEXT NOT NULL COMMENT '方药',
    dosage_instruction TEXT COMMENT '用法用量',
    treatment_course TEXT COMMENT '治疗经过',
    outcome TEXT COMMENT '治疗结果',
    doctor_name VARCHAR(50) COMMENT '医生姓名',
    hospital_name VARCHAR(100) COMMENT '医院名称',
    case_source VARCHAR(100) COMMENT '医案来源',
    tags TEXT COMMENT '标签（JSON格式）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_syndrome_diagnosis (syndrome_diagnosis),
    INDEX idx_doctor_name (doctor_name),
    INDEX idx_hospital_name (hospital_name),
    INDEX idx_is_active (is_active),
    FULLTEXT idx_content (chief_complaint, present_illness, symptoms, treatment_principle, prescription)
) ENGINE=InnoDB COMMENT='医案表';

-- 15. 系统配置表 (system_configs)
CREATE TABLE system_configs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT '配置类型',
    description TEXT COMMENT '配置描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_config_key (config_key),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='系统配置表';

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description) VALUES
('tcm_model_provider', 'DEEPSEEK_TCM', 'string', '中医模型提供商'),
('max_conversation_length', '100', 'number', '最大对话长度'),
('enable_tongue_analysis', 'true', 'boolean', '是否启用舌苔分析'),
('enable_prescription_check', 'true', 'boolean', '是否启用方剂配伍检查'),
('cache_ttl', '3600', 'number', '缓存过期时间（秒）'),
('max_file_size', '10485760', 'number', '最大文件大小（字节）'),
('supported_image_formats', '["jpg", "jpeg", "png", "bmp"]', 'json', '支持的图片格式');

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

-- 创建存储过程：获取患者最近病例
DELIMITER //
CREATE PROCEDURE GetPatientRecentCases(IN patient_id INT, IN limit_count INT)
BEGIN
    SELECT 
        mc.*,
        s.name as syndrome_name,
        s.description as syndrome_description
    FROM medical_cases mc
    LEFT JOIN syndromes s ON mc.syndrome_type = s.name
    WHERE mc.patient_id = patient_id
    ORDER BY mc.created_at DESC
    LIMIT limit_count;
END //
DELIMITER ;

-- 创建存储过程：更新药材库存
DELIMITER //
CREATE PROCEDURE UpdateHerbInventory(
    IN herb_id INT,
    IN quantity_change DECIMAL(10,3),
    IN operation_type ENUM('add', 'subtract')
)
BEGIN
    DECLARE current_quantity DECIMAL(10,3);
    
    SELECT quantity INTO current_quantity 
    FROM herb_inventory 
    WHERE herb_id = herb_id AND status = 'available'
    ORDER BY created_at DESC 
    LIMIT 1;
    
    IF operation_type = 'add' THEN
        UPDATE herb_inventory 
        SET quantity = quantity + quantity_change,
            updated_at = CURRENT_TIMESTAMP
        WHERE herb_id = herb_id AND status = 'available'
        ORDER BY created_at DESC 
        LIMIT 1;
    ELSE
        UPDATE herb_inventory 
        SET quantity = GREATEST(0, quantity - quantity_change),
            status = CASE 
                WHEN quantity - quantity_change <= 0 THEN 'out_of_stock'
                WHEN quantity - quantity_change <= 10 THEN 'low_stock'
                ELSE 'available'
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE herb_id = herb_id AND status = 'available'
        ORDER BY created_at DESC 
        LIMIT 1;
    END IF;
END //
DELIMITER ;

-- 创建触发器：自动更新对话消息计数
DELIMITER //
CREATE TRIGGER update_conversation_message_count
AFTER INSERT ON messages
FOR EACH ROW
BEGIN
    UPDATE conversations 
    SET total_messages = total_messages + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
END //
DELIMITER ;

-- 创建触发器：自动更新病例状态
DELIMITER //
CREATE TRIGGER update_case_status
BEFORE UPDATE ON medical_cases
FOR EACH ROW
BEGIN
    IF NEW.follow_up_date IS NOT NULL AND NEW.follow_up_date <= CURDATE() THEN
        SET NEW.status = 'completed';
    END IF;
END //
DELIMITER ;

-- 创建索引优化
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_medical_cases_patient_created ON medical_cases(patient_id, created_at);
CREATE INDEX idx_prescription_recommendations_user_created ON prescription_recommendations(user_id, created_at);
CREATE INDEX idx_tongue_analysis_user_created ON tongue_analysis(user_id, created_at);

-- 创建全文索引用于搜索
ALTER TABLE classic_texts ADD FULLTEXT(content, translation, annotation);
ALTER TABLE medical_records ADD FULLTEXT(chief_complaint, present_illness, treatment_principle, prescription);
ALTER TABLE herbs ADD FULLTEXT(name, effect, indication);

-- 设置字符集和排序规则
ALTER DATABASE tcm_agent_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 完成数据库初始化
SELECT 'SmartTCM-Agent 数据库初始化完成！' as message;
