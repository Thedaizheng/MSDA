import re
from utils.deepseek_api import call_deepseek

def generate_topic_outline_from_template(template_outline: str, topic: str, model: str = "deepseek-chat") -> list:
    """
    基于已有markdown大纲模板和用户给定的主题，调用LLM生成一个新的markdown大纲。
    """
    # 预处理模板，只保留markdown标题行
    template_headers = [line.strip() for line in template_outline.splitlines() if re.match(r'^#{1,6}\s', line.strip())]
    template_md = "\n".join(template_headers)

    # 构建 Prompt
    prompt = (
        f"你是一个专业的产业研究报告助手，现在请你参考以下Markdown格式的大纲模板，"
        f"重新为主题“{topic}”构建一个新的Markdown报告大纲。\n\n"
        f"要求：\n"
        f"1. 保持结构层级一致（如##、###）。\n"
        f"2. 保持逻辑结构合理，但内容要根据新主题调整。\n"
        f"3. 只输出大纲标题，不要正文内容。\n"
        f"4. 输出格式保持为 Markdown。\n\n"
        f"5. 构建的大纲标题需要有标题号，如1.1、1.1.1等，其中一级标题统一用汉字如一、二等等。\n\n"
        f"模板大纲如下：\n{template_md}"
    )

    response = call_deepseek(prompt, model=model)

    # 提取响应中的markdown标题
    output_headers = [line.strip() for line in response.splitlines() if re.match(r'^#{1,6}\s', line.strip())]
    return output_headers
