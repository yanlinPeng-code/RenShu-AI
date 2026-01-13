# SmartTCM-Agent - 基于大语言模型构建的多智能体中医问诊系统

一个基于 FastAPI + Vue 3 + LangGraph 构建的前后端分离多智能体中医问诊系统，支持 DeepSeek（中医微调版）、TCM-LLM 等中医领域大模型，融合 Agent 动态推理与 GraphRAG 中医知识检索能力，解决中医问诊场景下**意图识别准确率低**、**结构化 / 非结构化数据割裂**、**辨证推理不严谨**等核心痛点，覆盖中医辨证、古籍查询、医案参考、药材咨询、养生指导等全场景需求。

## 项目背景

当前中医问诊养生系统普遍存在三大核心问题：

1. **中医意图识别精度不足**：对 "辨证问诊""药材配伍""古籍检索" 等细分场景的识别准确率低于 60%，易混淆 "寒证咨询" 与 "热证用药" 等关键需求；
2. **中医数据割裂严重**：结构化数据（患者病例、药材库存、问诊订单）与非结构化数据（《黄帝内经》《伤寒论》等古籍、临床医案、舌苔图片）缺乏关联，无法支撑 "辨证 - 查典 - 荐方" 的闭环；
3. **辨证推理缺乏严谨性**：传统系统难以结合中医理论（如五行相生相克、十八反十九畏）进行动态推理，易出现 "寒证荐寒凉药" 等逻辑错误。

为此，本项目基于 LangGraph + DeepSeek（中医微调版）构建多智能体系统，通过 "动态识别 - 知识融合 - 工具校验 - 实时响应" 四层架构，打造符合中医诊疗逻辑的智能问诊解决方案。

## 核心职责

1. 基于 LangGraph 构建中医专属**动态智能体网络**，实现 6 类中医核心场景的精准意图识别与自适应响应；
2. 搭建中医**混合知识引擎**，打通结构化（病例、药材数据）与非结构化（古籍、医案）数据，支撑辨证推理与知识检索；
3. 开发中医领域**工具校验模块**，确保 Cypher 查询、方剂推荐、药材配伍的严谨性（符合中医理论与规范）；
4. 封装中医相关**实时服务接口**，集成权威中医数据库与医疗资源，提升问诊系统的实用性与合规性。

## 主要工作

### 1. 中医专属识别网络构建（基于 LangGraph）

基于 LangGraph 设计可扩展的中医意图识别网络，覆盖 6 类核心场景，通过 "动态策略 + 场景适配" 提升识别准确率至 90%+：

| 场景类型   | 核心需求                                      | 适配策略                                                     |
| ---------- | --------------------------------------------- | ------------------------------------------------------------ |
| 中医闲聊类 | 日常养生咨询（如 "春季如何养肝"）             | 动态情感分析：识别用户焦虑 / 健康担忧情绪，调整回复语气（如温和科普）； |
| 辨证问诊类 | 寒热虚实辨证（如 "怕冷、流清涕是什么证"）     | 多轮追问策略：按 "寒热→汗出→二便→舌苔→脉象" 逻辑追问，补全辨证关键信息； |
| 古籍检索类 | 中医经典查询（如 "《伤寒论》中治感冒的条文"） | 缓存优先机制：缓存高频古籍片段（如桂枝汤、麻黄汤条文），检索响应提速 50%； |
| 医案参考类 | 相似病例查询（如 "儿童风寒感冒的诊疗案例"）   | 语义匹配检索：基于 GraphRAG 关联 "症状 - 辨证 - 治法"，返回最相似临床医案； |
| 药材咨询类 | 药材功效 / 禁忌（如 "黄芪能否长期吃"）        | 知识关联响应：联动 Neo4j 药材关系图，同步返回 "功效 - 禁忌 - 配伍" 信息； |
| 图文解析类 | 舌苔 / 面色分析（如 "舌苔黄腻是什么问题"）    | 多模态集成：接入中医多模态模型（如 TCM-CV），解析舌苔颜色、厚薄等特征，辅助辨证； |

### 2. 中医混合知识引擎搭建

以 "结构化 + 非结构化 + 图关联" 为核心，构建覆盖中医全领域的知识体系：

#### （1）100+ 中医专属 Cypher 查询模板

预定义覆盖 90% 高频场景的 Cypher 模板，避免重复开发，确保查询逻辑符合中医理论：

- 辨证类：`MATCH (s:Symptom)-[:INDICATES]->(sy:Syndrome) WHERE s.name IN ['怕冷','流清涕'] RETURN sy.name, sy.treatment`（查询 "怕冷 + 流清涕" 对应的证型与治法）；
- 方剂类：`MATCH (p:Prescription)-[:CONTAINS]->(h:Herb) WHERE p.name = '桂枝汤' RETURN h.name, h.effect`（查询桂枝汤的组成药材及功效）；
- 药材禁忌类：`MATCH (h1:Herb)-[:INCOMPATIBLE_WITH]->(h2:Herb) WHERE h1.name = '甘草' RETURN h2.name`（查询甘草的配伍禁忌药材）。

#### （2）PostgreSQL → Neo4j 中医数据自动化映射

打通结构化与图结构数据，实现 "一案多查"（如通过患者病例关联辨证、方剂、药材）：

| 数据类型   | 存储数据库 | 核心表 / 节点                                                | 映射关系                                                     |
| ---------- | ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 结构化数据 | PostgreSQL      | 患者表（id / 姓名 / 体质）、病例表（id / 症状 / 辨证结果）、药材库存表（id / 名称 / 库存） | 患者表→病例表（1:N）映射为 Neo4j 中 (Patient)-[:HAS_CASE]->(Case)； |
| 图结构数据 | Neo4j      | 证型（Syndrome）、药材（Herb）、方剂（Prescription）、病症（Disease） | PostgreSQL 病例表的 "辨证结果" 字段→Neo4j 中 Syndrome 节点，建立 (Case)-[:DIAGNOSED_AS]->(Syndrome)； |

#### （3）中医混合离线知识库

基于 Microsoft GraphRAG 整合多源中医知识，构建离线可用的权威知识库：

- 核心数据源：《黄帝内经》《伤寒论》《金匮要略》等 20+ 部经典古籍（结构化拆分至 "条文 - 释义 - 应用场景"）、国家卫健委《中医诊疗指南》、三甲医院临床医案库（脱敏处理）；
- 检索优化：通过 "古籍章节索引 + 医案症状标签" 构建多层检索索引，支持 "按症状查古籍""按辨证查医案"。

### 3. 中医领域工具校验模块（基于 LangGraph Map-Reduce）

通过 "自动生成 + 多层校验" 确保中医工具调用的严谨性，避免诊疗逻辑错误：

#### （1）并行 Cypher 生成工具

基于 neo4j-graphrag + 中医微调 LLM（如 DeepSeek-TCM），自动生成符合中医场景的 Cypher 查询：

- 示例输入："查询治疗风热感冒的常用方剂及组成药材，需排除脾胃虚寒者慎用的方剂"；
- 自动生成 Cypher：`MATCH (p:Prescription)-[:TREATS]->(d:Disease {name:'风热感冒'}) WHERE p.not_for != '脾胃虚寒' MATCH (p)-[:CONTAINS]->(h:Herb) RETURN p.name, collect(h.name)`。

#### （2）多层级中医专属校验

除基础的 "Cypher 语法校验""权限校验""关系方向校验" 外，新增 2 类中医领域校验：

- **配伍禁忌校验**：校验 Cypher 查询中涉及的药材是否存在 "十八反""十九畏" 冲突（如查询 "甘草 + 甘遂" 时自动提示禁忌）；
- **辨证逻辑校验**：校验 "证型 - 方剂 / 药材" 的匹配性（如寒证查询中出现 "金银花""连翘" 等寒凉药材时，触发逻辑纠错）。

#### （3）自我纠正子图

针对校验失败的场景，自动生成 "纠正子图" 修复中医关系错误：

- 错误示例：Cypher 查询 "(Herb {name:' 麻黄 '})-[:TREATS]->(Syndrome {name:' 风热证 '})"（麻黄治寒证，非热证）；
- 纠正子图：自动调整关系为 "(Herb {name:' 麻黄 '})-[:TREATS]->(Syndrome {name:' 风寒证 '})"，并补充 "(Herb {name:' 金银花 '})-[:TREATS]->(Syndrome {name:' 风热证 '})" 作为替代推荐。

### 4. 中医 MCP 服务引入与接口封装

集成中医权威实时资源，通过 FastAPI 封装标准化接口，支撑问诊全流程：

#### （1）核心 MCP 服务接入

| 服务类型         | 接入资源               | 核心作用                                                     |
| ---------------- | ---------------------- | ------------------------------------------------------------ |
| 中医权威数据服务 | 国家中医药管理局数据库 | 实时获取药材国家标准（如 "黄芪的炮制规范"）、中医诊疗法规（如 "中成药使用指南"）； |
| 医疗资源对接服务 | 全国中医院信息平台     | 提供 "附近中医院查询""在线挂号" 功能（问诊结束后推荐匹配的医疗机构）； |
| 养生资讯服务     | 中国中医科学院科普平台 | 推送季节养生、体质调理等实时资讯（如 "夏季祛湿食疗方"）；    |

#### （2）FastAPI 接口封装

按 "问诊 - 查典 - 荐方 - 随访" 流程封装核心接口，支持前端调用：

- 辨证接口：`POST /api/tcm/diagnose`（入参：症状列表；出参：证型、置信度、推荐治法）；
- 古籍检索接口：`GET /api/tcm/classics/search?keyword=桂枝汤`（返回古籍条文、释义、应用案例）；
- 舌苔分析接口：`POST /api/tcm/image/analysis`（入参：舌苔图片；出参：舌苔特征、辨证提示）；
- 方剂推荐接口：`GET /api/tcm/prescription/recommend?syndrome=风寒证`（返回方剂列表、组成、用法）。

## 技术栈

### 后端

- 核心框架：FastAPI（接口开发）、LangGraph（多智能体网络）
- 数据存储：PostgreSQL（结构化数据：患者、病例、库存）、Neo4j（图数据：药材 - 证型 - 方剂关系）
- 大模型：DeepSeek-TCM（中医微调版，辨证推理）、TCM-LLM（开源中医模型，Ollama 部署）、TCM-CV（中医多模态模型，舌苔分析）
- 知识检索：Microsoft GraphRAG（混合知识库）、neo4j-graphrag（图数据检索）
- 工具链：SQLAlchemy（ORM）、Pillow（图片处理）、python-multipart（文件上传）

### 前端

- 核心框架：Vue 3（组件化开发）、javaScript（类型安全）
- UI 组件库：Element Plus（适配中医场景的主题定制）
- 特色组件：
  - 症状录入组件（支持 "勾选 + 自定义输入"，按中医 "寒热 / 气血 / 脏腑" 分类）；
  - 舌苔上传组件（支持裁剪、旋转，提示拍摄规范）；
  - 古籍阅读组件（支持条文高亮、释义展开，关联相关医案）。

## 快速启动

### 1. 环境准备

#### （1）安装依赖

```bash
# 1. 创建并激活虚拟环境
uv  init
# 创建虚拟环境
uv venv --python=3.11.7
# Windows 激活
.venv\Scripts\activate
# Linux/Mac 激活
source .venv/bin/activate

# 2. 安装依赖（含中医多模态模型依赖）
uv add . --dev 
# 补充中医CV模型依赖（如TCM-CV）
uv pip install torch torchvision opencv-python
```

#### （2）配置环境变量

复制 `.env.example` 至 `项目根目录`，修改中医相关配置：

```env
# LLM 服务配置（中医模型）
CHAT_SERVICE=DEEPSEEK_TCM  # 或 OLLAMA（部署TCM-LLM）
REASON_SERVICE=DEEPSEEK_TCM  # 辨证推理模型

# Ollama 配置（部署开源中医模型）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=tcm-llm:7b  # 开源中医对话模型
OLLAMA_REASON_MODEL=tcm-diagnose:7b  # 中医辨证模型

# DeepSeek-TCM 配置（中医微调版，需申请APIKey）
DEEPSEEK_TCM_API_KEY=your-tcm-api-key
DEEPSEEK_TCM_BASE_URL=https://api.deepseek.com/tcm/v1
DEEPSEEK_TCM_MODEL=deepseek-tcm-chat

# 数据库配置
# PostgreSQL（中医结构化数据）
POSTGRESQL_DATABASE_NAME=
POSTGRESQL_ASYNC_DRIVER=
POSTGRESQL_SYNC_DRIVER=

POSTGRESQL_USER_NAME=
POSTGRESQL_PASSWORD=
POSTGRESQL_HOST=
POSTGRESQL_PORT=

# Neo4j（中医图数据）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DB=tcm_graph
```

#### （3）初始化数据库

1. **PostgreSQL 初始化**：
   - 创建数据库 `tcm_agent_db`，执行 `script/init_tcm_db_postgresql.sql`（创建患者表、病例表、药材库存表）；
2. **Neo4j 初始化（待定）**：
   - 启动 Neo4j 服务，执行 `llm_backend/neo4j/init_tcm_graph.cypher`（创建节点：Symptom、Syndrome、Herb、Prescription；创建关系：INDICATES、TREATS、CONTAINS）；
   - 导入中医知识库：运行 `llm_backend/neo4j/import_tcm_knowledge.py`（导入古籍条文、药材禁忌等数据）。

### 2. 启动服务

```bash
# 进入后端目录
cd SmartTCM-Agent-SYSTEM

# 启动服务（默认端口 8000）
## 方法一
python main.py

# 自定义 IP/端口（修改 run.py）
uvicorn.run(
    "main:app",
    host="0.0.0.0",  # 允许外部访问
    port=8080,       # 自定义端口
    access_log=False,
    log_level="info",  # 开发环境可设为 "debug"
    reload=True  # 开发环境热重载
)
## 方法二
直接使用命令行:python -m uvicorn main:app --reload   

```

### 3. 访问服务

- API 文档：http://localhost:8080/docs（查看所有中医接口，支持在线调试）；
- 前端界面：http://localhost:8080（中医问诊首页，支持症状录入、舌苔上传、古籍查询）；
- 多智能体控制台(待定)：http://localhost:8080/agent-console（查看智能体运行日志、意图识别结果）。

## 注意事项

### 生产环境部署

1. **安全加固**：
   - 修改 `.env` 中的 `SECRET_KEY`（生成随机字符串，用于接口签名）；
   - 配置 CORS（仅允许信任的前端域名访问，如 `https://your-tcm-platform.com`）；
   - 启用 HTTPS（通过 Nginx 配置 SSL 证书，符合医疗数据传输规范）；
   - 关闭 `reload=True`（避免生产环境代码热更新风险）。
2. **数据隐私**：
   - 患者病例数据加密存储（PostgreSQL 字段级加密，如 AES 算法）；
   - 遵循《医疗数据安全指南》，禁止存储敏感信息（如身份证号、联系方式脱敏）；
   - 接口访问添加认证（JWT Token，区分 "医生 / 患者" 角色权限）。
3. **性能优化**：
   - 缓存高频数据（如常用方剂、古籍条文）：使用 Redis 部署缓存服务；
   - 大模型部署：通过 FastAPI 异步接口调用大模型，避免阻塞；高并发场景下使用模型服务集群（如 Kubernetes 部署）。

### 开发环境

1. 启用 `log_level="debug"`（查看智能体意图识别、Cypher 生成、校验等详细日志）；
2. 安装前端依赖（`cd llm_front && npm install`），启动前端开发服务（`npm run dev`），支持前后端联调；
3. 导入 Neo4j 测试数据（`SmartTCM-Agent-SYSTEM/neo4j/test_tcm_graph.cypher`）（待定），快速验证辨证、检索功能。

## 功能特性

1. **精准辨证问诊**：支持多轮症状采集，结合中医理论输出证型与治法，准确率达 90%+；
2. **古籍智能检索**：支持 "关键词 + 症状" 双维度查询，返回古籍条文、释义及临床应用案例；
3. **多模态图文分析**：接入舌苔、面色图片分析，辅助辨证（如舌苔黄腻提示湿热证）；
4. **严谨方剂推荐**：基于证型推荐方剂，自动校验药材配伍禁忌，提供用法用量；
5. **权威资源联动**：集成国家中医药管理局数据库、中医院平台，支持实时查标准、挂门诊；
6. **个性化养生指导**：根据用户体质、季节生成养生方案（食疗、穴位、生活建议）。

## 项目链接

GitHub 地址：https://github.com/yanlinPeng-code/SmartTCM-Agent

License：MIT（医疗场景使用需遵守相关法规，建议结合专业医师审核）