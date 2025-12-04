import re
import json
from doc_handler import base
from utils.deepseek_api import call_deepseek
from doc_handler.base import BaseDocHandler, Session


class Formatter(base.BaseDocHandler):
    def run(self, sess: Session):
        text = sess.text.strip()

        def extract_markdown_headers(content: str) -> list:
            return [line.strip() for line in content.splitlines() if re.match(r'^#{1,6}\s', line.strip())]

        def split_text_to_chunks(text: str, max_chunk_size: int = 3000) -> list:
            paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
            chunks, current_chunk = [], ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            if current_chunk:
                chunks.append(current_chunk.strip())
            return chunks

        # ✅ 情况 1：包含 Markdown 标题
        if any(re.match(r'^#{1,6}\s', line.strip()) for line in text.splitlines()):
            headers = extract_markdown_headers(text)
            sess.title = "\n".join(headers)
            return

        # ✅ 情况 2：无标题结构，需要调用大语言模型生成
        chunks = split_text_to_chunks(text)
        all_titles = []

        for chunk in chunks:
            prompt = (
                f"请你根据以下产业类正文内容，概括并生成一段符合 Markdown 报告结构的大纲，仅包含标题，特别注意与主题无关的小标题均删除，若有标题号需要保留，格式示例如下：\n"
                f"# 报告标题\n## 一级标题\n### 二级标题\n\n"
                f"正文如下：\n{chunk}"
            )
            response = call_deepseek(prompt, model="deepseek-chat")
            headers = extract_markdown_headers(response)
            all_titles.extend(headers)

        # 去重并保持顺序
        seen, unique_titles = set(), []
        for title in all_titles:
            if title not in seen:
                seen.add(title)
                unique_titles.append(title)

        sess.title = "\n".join(unique_titles)
