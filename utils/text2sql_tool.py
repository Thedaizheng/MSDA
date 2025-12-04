# utils/text2sql_tool.py

import os
import pymysql
from dotenv import load_dotenv
from utils.deepseek_api import call_deepseek  # ✅ 使用你写的接口函数

load_dotenv()


def generate_sql_from_question(question: str, schema_file_path="E:/DTG/sql.sql") -> str:
    try:
        with open(schema_file_path, "r", encoding="utf-8") as f:
            schema_content = f.read()

        prompt = f"""
你是一个SQL专家，请根据下列MySQL表结构，为用户的问题生成一个对应的SQL查询语句。

【表结构】
{schema_content}

【用户问题】
{question}

请只返回可执行的SQL语句，不要任何解释：
"""

        content = call_deepseek(prompt, model="deepseek-chat")
        sql = content.strip().strip("```sql").strip("```").strip()

        print(f"[Text2SQL] 生成的 SQL:\n{sql}")
        return sql

    except Exception as e:
        print(f"[Text2SQL] SQL生成失败：{e}")
        return None


def execute_sql(sql: str) -> str:
    if not sql:
        return "[Text2SQL] 无可执行SQL。"

    try:
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "123456"),
            database=os.getenv("MYSQL_DB", "storm_wiki_test"),
            charset="utf8mb4"
        )
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if not rows:
                return "[Text2SQL] 没有查询到结果。"

            # 获取字段名并格式化
            col_names = [desc[0] for desc in cursor.description]
            result_lines = ["\t".join(col_names)]
            for row in rows:
                result_lines.append("\t".join(str(cell) for cell in row))

            return "[Text2SQL] 查询结果：\n" + "\n".join(result_lines)

    except Exception as e:
        return f"[Text2SQL] 执行失败：{e}"

    finally:
        try:
            if conn:
                conn.close()
        except:
            pass


def query_text2sql(question: str) -> str:
    sql = generate_sql_from_question(question)
    result = execute_sql(sql)
    return result
