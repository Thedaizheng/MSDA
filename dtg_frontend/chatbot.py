import json
import subprocess
import requests
from doc_handler import doc_handler
from dtg_frontend import chatbot_ui
from utils.deepseek_api import call_deepseek


class Chatbot:
    def __init__(self):
        self.name = "dz团队的智能报告生成助手"

    def generate_ui(self):
        chatbotUI = chatbot_ui.ChatbotUI(self)
        return chatbotUI.generate_ui()

    def need_modify_report(self, user_message):
        keywords = ["增加", "完善", "改写", "补充", "总结", "优化", "调整", "重写", "删除"]
        return any(kw in user_message for kw in keywords)

    def handle_uploaded_file(self, file):
        res = doc_handler.instance.handle_doc(file)
        return res

    def stream_chat_with_deepseek(self, prompt):
        try:
            response = call_deepseek(prompt)
            for token in response:
                yield token
        except Exception as e:
            print("调用 Deepseek 出错:", e)
            yield "[发生错误，请检查 Deepseek 服务是否正常。]"

    def handle_topic(self, topic, model, api_key, title):
        try:
            subprocess.run([
                'python',
                'main.py',
                '--topic', topic,
                '--do-research',
                '--do-outline',
                '--do-write',
                '--do-polish'
            ], check=True)  # 添加 check=True，遇到错误会抛异常
        except Exception as e:
            print("执行 main.py 出错:", e)
            return "[报告生成失败，请检查运行日志]"

        # 返回完整内容
        return self.read_article_content(topic)

    def read_article_content(self, topic):
        filepath = f'output_test/article_polished_{topic}.txt'
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print("读取文章失败:", e)
            return "[读取生成的文章内容失败，请检查文件路径和内容是否存在。]"

