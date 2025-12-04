from utils.deepseek_api import call_deepseek

def generate_outline(topic: str, template_structure: list) -> str:
    prompt = f"""你是一个报告大纲规划专家。请参考以下报告结构：
{chr(10).join(template_structure)}

现在请基于用户提供的主题：{topic}，并借鉴以上结构，仅借鉴广度和深度，重新设计一个报告的Markdown标题大纲，大纲严格按照{topic}生成，尽量只保留到三级标题。
请确保所有标题严格使用Markdown语法（#、##、###）且不要有开头和结尾的多余字符或空行，只返回干净的标题内容。"""

    outline = call_deepseek(prompt)

    # 1. 去除开头结尾空白字符（换行、空格）
    outline = outline.strip()

    # 2. 对每行去除多余空格（可选）
    lines = [line.strip() for line in outline.splitlines() if line.strip()]
    outline_clean = "\n".join(lines)

    with open(f"output_test/outline_{topic}.txt", "w", encoding="utf-8") as f:
        f.write(outline_clean)

    return outline_clean
