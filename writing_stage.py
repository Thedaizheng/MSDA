from utils.rag_tool import query_rag
from utils.text2sql_tool import query_text2sql
from utils.tavily_search import tavily_search
from utils.deepseek_api import call_deepseek
import re
import csv
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import concurrent.futures


import os
import csv
import logging
import concurrent.futures

# 设置日志格式和级别
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class WriterAgent:
    def __init__(self, csv_path="output_test/result.csv"):
        print("[WriterAgent] 初始化写作代理")
        self.csv_path = csv_path
        self._init_csv_file()

    def _init_csv_file(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "标题", "信息来源", "Entity Recall", "标题相关性"
                ])

    def write_article(self, outline_titles, topic):
        print(f"[WriterAgent] 开始写作，章节数：{len(outline_titles)}")
        article = ""

        for title in outline_titles:
            print(f"[WriterAgent] 处理标题: {title}")
            clean_title = title.lstrip("#").strip()
            article += f"{clean_title}\n"

            if title.startswith("##"):
                content = self._generate_content(clean_title, topic)
                article += content + "\n"

        print("[WriterAgent] 写作完成")
        print("生成文章如下：",article)
        return article

    def _generate_content(self, title, topic):
        print(f"[WriterAgent] _generate_content 被调用，标题：{title}")
        combined_sources = {}

        # 定义单个查询函数
        def fetch_text2sql():
            try:
                print("[并发] Text2SQL 查询中...")
                result = query_text2sql(f"{title} 相关数据和分析").strip()
                return "text2sql", result
            except Exception as e:
                print(f"[Text2SQL 失败] {e}")
                return "text2sql", ""

        def fetch_rag():
            try:
                print("[并发] RAG 查询中...")
                result = query_rag(f"{title} 的背景、趋势或技术介绍").strip()
                return "rag", result
            except Exception as e:
                print(f"[RAG 失败] {e}")
                return "rag", ""

        def fetch_tavily():
            try:
                print("[并发] Tavily 搜索中...")
                result = tavily_search(f"{title} 的最新情况或企业动态").strip()
                return "tavily", result
            except Exception as e:
                print(f"[Tavily 失败] {e}")
                return "tavily", ""

        # 并行执行三个查询
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fn) for fn in [fetch_text2sql, fetch_rag, fetch_tavily]]
            for future in concurrent.futures.as_completed(futures):
                key, result = future.result()
                if result:
                    combined_sources[key] = result
                    print(f"[{key}] 获取成功")

        if not combined_sources:
            print("[WriterAgent] 未能获取到任何信息源，返回提示内容")
            return "【未能获取到有效数据，暂无法生成内容】"

        # 合并前 3 个来源的文本（每个截取前 1000 字，最多拼接 3000 字）
        combined_text = "\n\n".join(text[:1000] for text in combined_sources.values())[:3000]
        combined_source_keys = "+".join(combined_sources.keys())

        prompt = (
            f"你是一位专业产业研究员，请参考以下信息内容，为“{topic}”产业报告章节“{title}”撰写一段专业、结构清晰、语言正式的分析段落。\n\n"
            f"要求：不得编造数据，对于不确定的统计值请省略具体数值，生成内容需要在200-500字之间，首先需要满足与章节标题相关。\n\n"
            f"信息参考：\n{combined_text}\n\n请生成："
        )

        try:
            result = call_deepseek(prompt).strip()
            cleaned = self._clean_markdown_symbols(result)
            print(f"[WriterAgent] 章节 {title} 的内容为:\n{cleaned}")
            self._evaluate_and_save_metrics(title, combined_text, cleaned, combined_source_keys)
            return cleaned
        except Exception as e:
            print(f"[WriterAgent] 正文生成失败：{str(e)}")
            return f"【正文生成失败：{str(e)}】"


    def _clean_markdown_symbols(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        text = re.sub(r"-\s+", "• ", text)
        text = re.sub(r"^\s*\|\s*.*\s*\|\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\|", " ", text)
        text = re.sub(r":?-+:?", "", text)
        return text.strip()

    def _evaluate_and_save_metrics(self, title, source, generated, source_type):
        source_keywords = self.extract_keywords(source, top_k=50)
        generated_keywords = self.extract_keywords(generated, top_k=50)

        entity_match_count = self.count_fuzzy_matches(source_keywords, generated_keywords)

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([title, generated])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

        print(f"[评估] Entity Match Count: {entity_match_count}, 标题相关性: {similarity:.2f}")
        print(f"[调试] Source Keywords: {source_keywords}")
        print(f"[调试] Generated Keywords: {generated_keywords}")

        with open(self.csv_path, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                title, source_type,
                f"{entity_match_count}",
                f"{similarity:.4f}"
            ])

    def count_fuzzy_matches(self, source_keywords, generated_keywords):
        match_count = 0
        for src_kw in source_keywords:
            for gen_kw in generated_keywords:
                if src_kw in gen_kw or gen_kw in src_kw:
                    match_count += 1
                    break
        return match_count

    def extract_keywords(self, text, top_k=50):
        tokens = jieba.lcut(text)
        tokens = [t for t in tokens if len(t) >= 2]
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [token for token, _ in sorted_tokens[:top_k]]


class WriterAgent_sdtg:
    def __init__(self, csv_path="result/result_8.csv"):
        print("[WriterAgent] 初始化写作代理")
        self.csv_path = csv_path
        self._init_csv_file()

    def _init_csv_file(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "标题", "信息来源", "Entity Recall", "标题相关性"
                ])

    def write_article(self, outline_titles, topic):
        print(f"[WriterAgent] 开始写作，章节数：{len(outline_titles)}")
        article = ""

        for title in outline_titles:
            print(f"[WriterAgent] 处理标题: {title}")
            clean_title = title.lstrip("#").strip()
            article += f"{clean_title}\n"

            if title.startswith("##"):
                content = self._generate_content(clean_title, topic)
                article += content + "\n"

        print("[WriterAgent] 写作完成")
        return article

    def _generate_content(self, title, topic):
        print(f"[WriterAgent] _generate_content 被调用，标题：{title}")
        sources = {}

        try:
            print(f"[WriterAgent] 正在调用 Tavily 搜索...")
            web_info = tavily_search(f"{title} 的最新情况或企业动态")
            if web_info.strip():
                sources["tavily"] = web_info
                print("[WriterAgent] Tavily 搜索成功")
        except Exception as e:
            print(f"[Tavily 失败] {e}")

        if "tavily" not in sources:
            print("[WriterAgent] 未能获取到有效数据，返回提示内容")
            return "【未能获取到有效数据，暂无法生成内容】"

        input_content = sources["tavily"][:2000]
        prompt = (
            f"你是一位专业产业研究员，请参考以下信息内容，为{topic}报告章节“{title}”撰写一段专业、结构清晰、语言正式的分析段落。\n\n"
            f"要求：不得编造数据，对于不确定的统计值请省略具体数值，生成内容需要在200-500字之间。\n\n"
            f"信息参考：\n{input_content}\n\n请生成："
        )

        try:
            result = call_deepseek(prompt).strip()
            cleaned = self._clean_markdown_symbols(result)
            print(f"[WriterAgent] 章节{title}的内容为:\n{cleaned}")
            self._evaluate_and_save_metrics(title, input_content, cleaned, "tavily")
            return cleaned
        except Exception as e:
            print(f"[WriterAgent] 正文生成失败：{str(e)}")
            return f"【正文生成失败：{str(e)}】"

    def _clean_markdown_symbols(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        text = re.sub(r"-\s+", "• ", text)
        text = re.sub(r"^\s*\|\s*.*\s*\|\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\|", " ", text)
        text = re.sub(r":?-+:?", "", text)
        return text.strip()

    def _evaluate_and_save_metrics(self, title, source, generated, source_type):
        source_keywords = self.extract_keywords(source, top_k=50)
        generated_keywords = self.extract_keywords(generated, top_k=50)

        entity_match_count = self.count_fuzzy_matches(source_keywords, generated_keywords)

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([title, generated])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

        print(f"[评估] Entity Match Count: {entity_match_count}, 标题相关性: {similarity:.2f}")
        print(f"[调试] Source Keywords: {source_keywords}")
        print(f"[调试] Generated Keywords: {generated_keywords}")

        with open(self.csv_path, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                title, source_type,
                f"{entity_match_count}",
                f"{similarity:.4f}"
            ])

    def count_fuzzy_matches(self, source_keywords, generated_keywords):
        match_count = 0
        for src_kw in source_keywords:
            for gen_kw in generated_keywords:
                if src_kw in gen_kw or gen_kw in src_kw:
                    match_count += 1
                    break
        return match_count

    def extract_keywords(self, text, top_k=50):
        tokens = jieba.lcut(text)
        tokens = [t for t in tokens if len(t) >= 2]
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [token for token, _ in sorted_tokens[:top_k]]


class WriterAgent_tllm:
    def __init__(self, csv_path="result/result_12.csv"):
        print("[WriterAgent] 初始化写作代理")
        self.csv_path = csv_path
        self._init_csv_file()

    def _init_csv_file(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "标题", "信息来源", "Entity Recall", "标题相关性"
                ])

    def write_article(self, outline_titles, topic):
        print(f"[WriterAgent] 开始写作，章节数：{len(outline_titles)}")
        article = ""

        for title in outline_titles:
            print(f"[WriterAgent] 处理标题: {title}")
            clean_title = title.lstrip("#").strip()
            article += f"{clean_title}\n"

            if title.startswith("##"):
                content = self._generate_content(clean_title, topic)
                article += content + "\n"

        print("[WriterAgent] 写作完成")
        return article

    def _generate_content(self, title, topic):
        print(f"[WriterAgent] _generate_content 被调用，标题：{title}")

        prompt = (
            f"你是一位专业产业研究员，请为“{topic}”产业报告章节“{title}”撰写一段专业、结构清晰、语言正式的分析段落。\n\n"
            f"要求：不得编造数据，对于不确定的统计值请省略具体数值，生成内容需要在200-500字之间。\n\n"
            f"请生成："
        )

        try:
            result = call_deepseek(prompt).strip()
            cleaned = self._clean_markdown_symbols(result)
            print(f"[WriterAgent] 章节{title}的内容为:\n{cleaned}")
            self._evaluate_and_save_metrics(title, prompt, cleaned, "llm")
            return cleaned
        except Exception as e:
            print(f"[WriterAgent] 正文生成失败：{str(e)}")
            return f"【正文生成失败：{str(e)}】"

    def _clean_markdown_symbols(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        text = re.sub(r"-\s+", "• ", text)
        text = re.sub(r"^\s*\|\s*.*\s*\|\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\|", " ", text)
        text = re.sub(r":?-+:?", "", text)
        return text.strip()

    def _evaluate_and_save_metrics(self, title, source, generated, source_type):
        source_keywords = self.extract_keywords(source, top_k=50)
        generated_keywords = self.extract_keywords(generated, top_k=50)

        entity_match_count = self.count_fuzzy_matches(source_keywords, generated_keywords)

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([title, generated])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

        print(f"[评估] Entity Match Count: {entity_match_count}, 标题相关性: {similarity:.2f}")
        print(f"[调试] Source Keywords: {source_keywords}")
        print(f"[调试] Generated Keywords: {generated_keywords}")

        with open(self.csv_path, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                title, source_type,
                f"{entity_match_count}",
                f"{similarity:.4f}"
            ])

    def count_fuzzy_matches(self, source_keywords, generated_keywords):
        match_count = 0
        for src_kw in source_keywords:
            for gen_kw in generated_keywords:
                if src_kw in gen_kw or gen_kw in src_kw:
                    match_count += 1
                    break
        return match_count

    def extract_keywords(self, text, top_k=50):
        tokens = jieba.lcut(text)
        tokens = [t for t in tokens if len(t) >= 2]
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [token for token, _ in sorted_tokens[:top_k]]
