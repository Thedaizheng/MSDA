from docx import Document

import os
import PyPDF2
import docx

from doc_handler.base import BaseDocHandler, Session

class Reader(BaseDocHandler):
    def run(self, sess: Session):
        file_path = sess.file_name
        ext = os.path.splitext(file_path)[-1].lower()

        try:
            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    sess.text = f.read()

            elif ext == ".pdf":
                content = ""
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content += page.extract_text() or ""
                sess.text = content

            elif ext == ".docx":
                doc = docx.Document(file_path)
                sess.text = "\n".join([para.text for para in doc.paragraphs])

            else:
                sess.text = f"不支持的文件格式：{ext}"

        except Exception as e:
            sess.text = f"读取文件时出错：{str(e)}"

