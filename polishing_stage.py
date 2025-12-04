import re
from utils.deepseek_api import call_deepseek
import logging

def split_article_by_chapter(article: str) -> list:
    # 更强大的章节标题识别：匹配开头有换行或文首 + “一、标题” 或 “第一章 标题”
    pattern = r'(?=(?:^|\n)([一二三四五六七八九十百千万零〇两]{1,5}[、.．．])[\s\S]*?)'

    matches = list(re.finditer(pattern, article))

    if not matches:
        print("[split_article_by_chapter] 未找到任何章节标题")
        return []

    chunks = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(article)
        chunk = article[start:end].strip()
        chunks.append(chunk)

    print(f"[split_article_by_chapter] 拆分成功，章节数: {len(chunks)}")
    return chunks


def polish_article(article: str, topic: str) -> str:
    chunks = split_article_by_chapter(article)
    if not chunks:
        print("[polish_article] 文章未按章节拆分成功")
        return ""

    polished_chunks = []

    for i, chunk in enumerate(chunks):
        prompt = (f"请对以下文章段落进行清理，如果有重复的多余标题进行删除，最后只保留Markdown格式的内容，并且不要出现任何与报告内容无关的系统提示和标注仅返回内容即可"
                  f"，可以适当将数据转换为表格，但不能整个章节内容"
                  f"全部都是表格，需要有对应的文字说明：\n\n{chunk}")
        try:
            polished = call_deepseek(prompt).strip()
            if not polished:
                logging.warning(f"[第{i+1}段] call_deepseek 返回空内容")
                continue
            polished_chunks.append(polished)
        except Exception as e:
            logging.error(f"[第{i+1}段] 润色失败：{e}")
            continue

    final_output = '\n\n'.join(polished_chunks).strip()

    # # 打印调试信息
    # print(f"[polish_article] 最终润色段落数: {len(polished_chunks)}")
    # print(f"[polish_article] 内容长度: {len(final_output)}")
    #
    # if not final_output:
    #     print("[polish_article] 最终结果为空，未写入文件")
    #     return "【润色失败】"

    output_path = f"output_test/article_polished_{topic}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_output)

    print(f"[polish_article] 写入文件成功: {output_path}")
    return final_output

