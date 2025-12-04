from fastapi import FastAPI
import random
import uvicorn
import gradio as gr
import openai
import os
from dtg_frontend import chatbot_ui
from markdown import markdown  # ✅ 导入的是函数，不是模块
from bs4 import BeautifulSoup
from docx import Document
import tempfile

css = """
        .gradio-container {
            background-color: #001f3f; /* 深蓝色背景 */
        }
        h1 { 
            color: white !important; /* 标题字体颜色为白色 */
            margin-top: 20px;        /* 增加顶部间距 */
            margin-bottom: 20px;     /* 增加底部间距 */
        }
        #chat-panel {
            position: fixed !important;
            top: 0;
            right: 0;
            width: 350px;
            height: 100%;
            background-color: #fefefe;
            box-shadow: -2px 0 8px rgba(0, 0, 0, 0.2);
            padding: 20px;
            overflow-y: auto;
            z-index: 9999;
        }
        
        #open-chat-btn {
            position: fixed !important;
            top: 20px;
            right: 20px;
            z-index: 10000;
        }

    """


class ChatbotUI():
    def __init__(self, chatbot):
        self.chatbot = chatbot

    def generate_ui(self):
        with gr.Blocks(css=css) as gr_service:
            gr.Markdown(
                f"<h1 style='text-align: center;'>智能报告生成助手</h1>"
            )

            with gr.Row():
                # 左侧设置栏
                with gr.Column(scale=1, min_width=300):
                    gr.Image(value="dtg_frontend/chatbot_img.webp", interactive=False, show_label=False,
                             height=150, elem_id="logo")

                    upload_file = gr.File(
                        label="上传参考模板（支持pdf/word/txt）",
                        file_types=[".pdf", ".docx", ".txt"],
                        file_count="single",
                        scale=0,
                        interactive=True,
                        elem_id="upload-box"
                    )
                    # 在此定义 output，显示文件解析后的结果
                    title = gr.Textbox(label="文件小标题", lines=5, interactive=False)
                    # 绑定上传文件事件，当文件上传后调用 handle_uploaded_file
                    upload_file.change(
                        fn=self.handle_uploaded_file,
                        inputs=[upload_file],
                        outputs=[title],  # 输出解析的小标题到 output
                    )

                    model = gr.Dropdown(label="模型选择",
                                        choices=["默认使用系统服务器模型", "Openai", "Deepseek", "Qwen", "claude"],
                                        value="默认使用系统服务器模型")
                    api_key = gr.Textbox(label="API_KEY",
                                         placeholder="请输入您选择模型的APIKEY...(系统模型无需APIKEY)")
                    creativity = gr.Slider(minimum=0.0, maximum=2.0, value=0.7, step=0.1, label="创造力")

                # 右侧主操作区
                with gr.Column(scale=3):
                    topic = gr.Textbox(label="报告主题", placeholder="请输入您要生成的报告主题...", lines=1)

                    with gr.Row():
                        report_type = gr.Dropdown(label="报告类型",
                                                  choices=["技术报告", "市场调研", "学术报告", "总结报告"],
                                                  value="技术报告")
                        language = gr.Dropdown(label="语言", choices=["中文", "英文"], value="中文")
                        style = gr.Dropdown(label="写作风格", choices=["正式", "轻松", "学术"], value="正式")

                    length = gr.Slider(label="预计字数", minimum=200, maximum=3000, value=1000, step=30)

                    output = gr.Textbox(label="生成的报告", lines=20, interactive=True, show_copy_button=True)

                    with gr.Row():
                        generate_btn = gr.Button("生成报告")
                        clear_btn = gr.ClearButton([topic, output])
                    with gr.Row():
                        download_btn = gr.Button("下载报告")

                    download_file = gr.File(label="下载生成的报告", visible=False)

                    generate_btn.click(
                        self._handle_generate_report,
                        inputs=[topic, report_type, language, style, length, model, api_key, creativity, title],
                        outputs=[output],
                        queue=True
                    )
                    download_btn.click(
                        fn=self.save_report_to_file,
                        inputs=[output],
                        outputs=[download_file])

            chat_panel_visible = gr.State(value=False)  # 控制侧边栏显示状态
            with gr.Row():
                open_chat_btn = gr.Button("🗨️ 打开智能对话", elem_id="open-chat-btn")
            with gr.Column(visible=False, elem_id="chat-panel") as chat_sidebar:
                gr.Markdown("### 💬 智能助手对话")
                chatbot_history = gr.Chatbot(label="聊天记录", height=400)
                chat_input = gr.Textbox(placeholder="请输入您的问题...", label="与AI对话", lines=1)
                send_btn = gr.Button("发送")

                send_btn.click(
                    self._handle_chat_interaction,
                    inputs=[chat_input, chatbot_history, model, api_key],
                    outputs=[chatbot_history, chat_input],
                    queue=True
                )
                open_chat_btn.click(
                    lambda visible: not visible,
                    inputs=[chat_panel_visible],
                    outputs=[chat_panel_visible],
                ).then(
                    lambda visible: gr.update(visible=visible),
                    inputs=[chat_panel_visible],
                    outputs=[chat_sidebar]
                )

        return gr_service.queue()

    def _handle_generate_report(self, topic, report_type, language, style, length, model, api_key, creativity, title):
        yield gr.update(value="正在生成报告，请稍候...")
        print(title)
        context = self.chatbot.handle_topic(topic, model, api_key, title)
        yield gr.update(value=context)

    # 将 markdown_to_text 改回实例方法
    def markdown_to_text(self, markdown_string):
        html = markdown(markdown_string)
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

    def save_report_to_file(self, report_text):
        # 转换 Markdown 为纯文本
        plain_text = self.markdown_to_text(report_text)

        # 创建 Word 文档
        doc = Document()
        doc.add_paragraph(plain_text)

        # 生成文件路径
        static_path = "static/reports"
        os.makedirs(static_path, exist_ok=True)  # 确保静态文件夹存在
        file_path = os.path.join(static_path, "generated_report.docx")

        # 保存到指定文件夹
        doc.save(file_path)

        # 返回 gr.File 组件，提供相对路径
        print(f"Generated file at: {file_path}")  # 输出生成文件路径
        return gr.File(value=file_path, visible=True)  # 返回文件路径，供 Gradio 下载并确保下载按钮可见

    def handle_uploaded_file(self, file):
        print("file's name is :", file)
        if file is None:
            return file
        result = self.chatbot.handle_uploaded_file(file)
        with open(r"E:\DTG\data\templates\temp.txt","w",encoding='utf-8') as f:
            f.write(result)
        return result

    def _handle_chat_interaction(self, message, chat_history, model, api_key, report_text):
        if not message or not report_text:
            yield chat_history, ""

        # 构建上下文 prompt
        prompt = f"""以下是已生成的报告内容：
                ---
                {report_text}
                ---
                请基于以上内容回答用户的问题：
                「{message}」
                """

        partial_response = ""
        updated_history = chat_history + [(message, "")]

        # 调用封装好的 Ollama 流式方法
        for token in self.chatbot.stream_chat_with_ollama(prompt):
            partial_response += token
            updated_history[-1] = (message, partial_response)
            yield updated_history, ""

