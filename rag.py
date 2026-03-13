import streamlit as st
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma
from zhipuai import ZhipuAI  # ← 修改：导入智谱 AI
import shutil

# ============== 配置 ==============
os.makedirs("uploads", exist_ok=True)
os.makedirs("chroma_db", exist_ok=True)

# ============== 页面配置 ==============
st.set_page_config(page_title="智能文档问答系统", page_icon="📚")
st.title("📚 智能文档问答系统")
st.markdown("上传 PDF/Word 文档，AI 基于文档内容回答问题")

# ============== 侧边栏 ==============
with st.sidebar:
    st.header("设置")
    
    # API Key 配置
    try:
        ZHIPU_API_KEY = st.secrets["ZHIPU_API_KEY"]  # ← 修改：智谱 API Key
    except:
        ZHIPU_API_KEY = st.text_input("智谱 AI API Key", type="password")
    
    if not ZHIPU_API_KEY:
        st.warning("⚠️ 请输入 API Key")
        st.stop()
    
    # 上传文件
    uploaded_file = st.file_uploader("上传文档", type=["pdf", "docx"])
    
    # 清空按钮
    if st.button("🗑️ 清空知识库"):
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
            os.makedirs("chroma_db")
        st.success("知识库已清空！")

# ============== 核心函数 ==============

@st.cache_resource
def load_document(file):
    """加载文档"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name
    
    if file.name.endswith(".pdf"):
        loader = PyPDFLoader(tmp_path)
    elif file.name.endswith(".docx"):
        loader = Docx2txtLoader(tmp_path)
    else:
        return []
    
    documents = loader.load()
    os.unlink(tmp_path)
    return documents

@st.cache_resource
def split_documents(documents):
    """文本分块"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    return text_splitter.split_documents(documents)

@st.cache_resource
def create_vectorstore(documents):
    """创建向量数据库"""
    embeddings = FakeEmbeddings(size=128)
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vectorstore

def query_document(vectorstore, question, api_key):
    """查询文档并生成回答"""
    # 检索相关文档
    docs = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # ← 修改：使用智谱 AI 调用
    client = ZhipuAI(api_key=api_key)
    prompt = f"""基于以下文档内容回答问题。如果文档中没有相关信息，请说"文档中没有相关信息"。

文档内容：
{context}

问题：{question}

回答："""
    
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    
    return answer, docs

# ============== 主界面 ==============

if uploaded_file:
    st.sidebar.success(f"✅ 已上传：{uploaded_file.name}")
    
    with st.spinner("📖 正在加载文档..."):
        documents = load_document(uploaded_file)
    
    if documents:
        st.sidebar.info(f"📄 共 {len(documents)} 页")
        
        with st.spinner("✂️ 正在分块处理..."):
            chunks = split_documents(documents)
        st.sidebar.info(f"✂️ 共 {len(chunks)} 个文本块")
        
        with st.spinner("🗄️ 正在构建知识库..."):
            vectorstore = create_vectorstore(chunks)
        st.sidebar.success("✅ 知识库构建完成！")
        
        st.divider()
        st.subheader("💬 开始提问")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if question := st.chat_input("请输入你的问题..."):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            with st.chat_message("assistant"):
                with st.spinner("🤖 正在思考..."):
                    answer, source_docs = query_document(vectorstore, question, ZHIPU_API_KEY)
                    st.markdown(answer)
                    
                    with st.expander("📖 查看参考来源"):
                        for i, doc in enumerate(source_docs, 1):
                            st.markdown(f"**来源 {i}:**")
                            st.markdown(doc.page_content[:200] + "...")
            
            st.session_state.messages.append({"role": "assistant", "content": answer})

else:
    st.info("👈 请在左侧上传 PDF 或 Word 文档")
    
    st.divider()
    st.subheader("💡 使用示例")
    st.markdown("""
    1. **上传公司手册** → 问"年假有多少天？"
    2. **上传产品文档** → 问"这个功能怎么用？"
    3. **上传论文** → 问"核心观点是什么？"
    4. **上传合同** → 问"付款条款是什么？"
    """)