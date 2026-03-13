# 📚 智能文档问答系统（RAG）

基于 LangChain + 向量数据库的文档智能问答系统

## 🎯 项目简介
用户上传 PDF/Word 文档，AI 基于文档内容回答问题。支持语义检索、多轮对话、参考来源展示。

## ✨ 功能特点
- 📄 支持 PDF/Word 文档上传
- 🔍 语义检索，精准定位相关段落
- 🤖 基于大模型生成回答
- 📖 展示参考来源，答案可追溯
- 💬 支持多轮对话和历史记录
- 🗑️ 一键清空知识库

## 🛠️ 技术栈
- **语言**: Python
- **界面**: Streamlit
- **大模型**: 智谱 AI (GLM-4)
- **向量库**: ChromaDB
- **文档处理**: LangChain, PyPDF, python-docx
- **嵌入模型**: FakeEmbeddings

## 🚀 在线演示
访问：https://rag-doc-qa.streamlit.app

## 📦 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/ireina201/rag-doc-qa.git
cd rag-doc-qa

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key（创建 .streamlit/secrets.toml）
ZHIPU_API_KEY = "你的智谱 API Key"

# 4. 运行应用
streamlit run rag.py