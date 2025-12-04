# utils/rag_tool.py

from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
from utils.deepseek_api import call_deepseek

load_dotenv()

# ✅ 初始化向量数据库
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory="E:/DTG/linyi_equipment_kb", embedding_function=embedding_model)


def query_rag(query: str) -> str:
    """
    基于向量检索，结合 DeepSeek 生成内容，加入日志信息辅助调试。
    """
    print(f"[RAG] 开始处理 query：{query}")

    try:
        # Step 1: 检索向量数据库
        docs = vectordb.similarity_search(query, k=5)
        print(f"[RAG] 检索到文档数量：{len(docs)}")

        if not docs:
            print("[RAG] 未找到相关资料。")
            return "[RAG] 未找到相关资料。"

        # Step 2: 拼接上下文内容
        context = "\n\n".join([doc.page_content for doc in docs])
        print("[RAG] 构建上下文内容成功。")

        # Step 3: 构建提示词并调用 DeepSeek
        prompt = f"""
你是一位产业研究专家，请结合以下背景资料，围绕“{query}”生成一段高质量的分析内容：

【背景资料】
{context}

【任务】
请撰写一段与上述主题相关的、结构清晰、用词准确的产业分析内容。
"""

        print("[RAG] 正在调用 DeepSeek 生成答案……")
        result = call_deepseek(prompt, model="deepseek-chat")
        print("[RAG] DeepSeek 返回内容成功。")

        return f"[RAG] {result.strip()}"

    except Exception as e:
        print(f"[RAG] 查询失败：{e}")
        return f"[RAG] 查询失败：{e}"
