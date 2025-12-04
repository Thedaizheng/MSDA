# utils/tavily_search.py

import os
import requests
from dotenv import load_dotenv
from utils.deepseek_api import call_deepseek

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def tavily_search(query: str) -> str:
    """
    使用 Tavily 搜索查询相关网页，并调用 DeepSeek 根据结果生成分析内容。
    """
    print(f"[TAVILY] 开始处理 query：{query}")

    try:
        # Step 1: Tavily 搜索
        tavily_url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_images": False,
            "max_results": 5
        }

        response = requests.post(tavily_url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        print(f"[TAVILY] 获取搜索结果成功，结果数：{len(results)}")

        if not results:
            print("[TAVILY] 未找到相关网页内容。")
            return "[TAVILY] 未找到相关网页内容。"

        # Step 2: 提取内容
        combined_content = "\n\n".join([f"{r['title']}\n{r['content']}" for r in results if r.get("content")])
        print("[TAVILY] 成功整合网页内容。")

        # Step 3: 构造提示词，调用 DeepSeek
        prompt = f"""
你是一位产业研究分析师，请根据以下最新网络搜索内容，围绕“{query}”撰写一段高质量的分析内容：

【网络资料】
{combined_content}

【任务】
请撰写一段客观、结构清晰、语言专业的分析内容，围绕上述主题展开。
"""
        print("[TAVILY] 正在调用 DeepSeek 生成内容……")
        answer = call_deepseek(prompt, model="deepseek-chat")
        print("[TAVILY] DeepSeek 返回成功。")

        return f"[TAVILY] {answer.strip()}"

    except Exception as e:
        print(f"[TAVILY] 查询失败：{e}")
        return f"[TAVILY] 查询失败：{e}"
