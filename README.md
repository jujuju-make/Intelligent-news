# IntelliNews-Agent: 基于 FastAPI 与 RAG 架构的智能资讯深度系统

本系统是一个为用户提供高效新闻阅读与智能交互的后端项目。不仅实现了基础的新闻管理功能，更集成了 **LLM Agent** 与 **RAG (检索增强生成)** 技术，使用户能够通过自然语言与私有新闻库进行深度对话。

## 🚀 项目核心亮点

- **RAG 架构实现**：集成 **ChromaDB** 向量数据库，通过阿里 **DashScope (通义千问)** 嵌入模型将 400+ 条新闻向量化，实现基于语义而非关键词的高精度检索。
- **智能意图识别**：通过大模型对用户输入进行实时解析（Intent Parsing），动态路由至数据库查询或通用对话逻辑。
- **上下文感知记忆**：设计了基于 **MySQL** 存储的“滑动窗口”对话记忆机制，确保 AI 能够理解多轮对话上下文。
- **高性能异步后端**：基于 **FastAPI** 异步框架，利用 `async/await` 实现非阻塞 I/O，优化了多模型调用的响应延迟。
- **工业级鉴权**：采用 **JWT (JSON Web Token)** 实现无状态身份认证，密码经过 **Bcrypt** 盐值哈希加密。

## 🛠 技术栈

- **语言**: Python 3.11+
- **框架**: FastAPI (Asynchronous)
- **数据库**: MySQL 8.0 (关系型), ChromaDB (向量数据库)
- **ORM**: SQLAlchemy 2.0 (Mapped Types)
- **AI/LLM**: OpenAI SDK, DashScope (Qwen-plus/max), Rerank API
- **工具**: Git (SSH), Apifox, Docker (规划中)

## 📁 项目结构预览

```text
├── config/         # 环境与数据库配置
├── crud/           # 数据库增删改查核心逻辑 (MySQL & ChromaDB)
├── models/         # SQLAlchemy 数据库模型定义
├── routers/        # API 路由分发 (User, News, AI Agent)
├── schemas/        # Pydantic 数据验证模型
├── utils/          # 工具类 (JWT鉴权、密码加密)
├── static/         # 静态资源 (用户头像等)
├── sync_data.py    # 数据同步脚本 (MySQL 文本转向量至 ChromaDB)
└── main.py         # 程序入口

如何在本地运行
1.克隆仓库：
git clone git@github.com:jujuju-make/Intelligent-news.git
cd Intelligent-news
2.安装依赖:
pip install -r requirements.txt
3.配置环境变量:
在根目录创建 .env 文件并填入：
ASYNC_DATABASE_URL=mysql+aiomysql://root:密码@localhost:3306/news_app
DASHSCOPE_API_KEY=你的阿里API密钥
SECRET_KEY=你的JWT加密密钥
4.同步向量数据:
python sync_data.py
5.启动服务:
uvicorn main:app --reload
