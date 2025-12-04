import argparse
from config import load_config
from template_parser import generate_topic_outline_from_template
from outline_generator import generate_outline
from writing_stage import WriterAgent,WriterAgent_sdtg,WriterAgent_tllm
from polishing_stage import polish_article
import logging
import sys
sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+

def main():
    parser = argparse.ArgumentParser(description="DTG Long Text Generation with Ollama")
    parser.add_argument('--topic', type=str, required=True, help='文章主题')
    parser.add_argument('--do-research', action='store_true', help='是否执行研究阶段')
    parser.add_argument('--do-outline', action='store_true', help='是否生成大纲')
    parser.add_argument('--do-write', action='store_true', help='是否进入写作阶段')
    parser.add_argument('--do-polish', action='store_true', help='是否润色文章')
    # parser.add_argument('--templete', type=str,action='store_true', help='是否润色文章')
    args = parser.parse_args()

    load_config()  # 加载环境变量及API密钥

    # 1. 解析模板

    with open(r"E:\MSDA-Text\data\templates\temp.txt","r",encoding='utf-8') as f:
        templete = f.read()
    template_structure = generate_topic_outline_from_template(templete,args.topic)

    # 2. 生成大纲
    # main.py 的相关片段示范

    if args.do_outline or args.do_research:
        outline_text = generate_outline(args.topic, template_structure)
        # 假设 generate_outline 返回的是多行字符串，需要拆成列表
        outline_titles = [line.strip() for line in outline_text.splitlines() if line.strip()]
    else:
        print("未启用大纲生成，程序结束")
        return
    # 3. 写作阶段
    article = ""
    if args.do_write:
        writer = WriterAgent()
        # writer = WriterAgent
        # _sdtg()
        # writer = WriterAgent_tllm()
        article = writer.write_article(outline_titles,args.topic)  # 传入标题列表
    # 4. 润色阶段
    print("article:",article)
    if args.do_polish and article:
        polished = polish_article(article,args.topic)
        print("润色后的文章:\n", polished)
        logging.info(f"润色后的文章：\n {polished}")
    else:
        print("生成文章:\n", article)
        logging.info(f"生成的文章：\n {article}")


if __name__ == "__main__":
    main()
