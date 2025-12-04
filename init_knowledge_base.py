from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def init_linyi_equipment_kb(doc_files, persist_dir="your_db"):
    """
    doc_files: 文本文件路径列表，内容关于临沂市高端装备产业
    persist_dir: 向量库持久化目录
    """

    # 1. 读取所有文本内容
    documents = []
    for file_path in doc_files:
        with open(file_path, "r", encoding="utf-8") as f:
            documents.append(f.read())

    # 2. 文本切分器（块大小1000，重叠100）
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for doc in documents:
        chunks.extend(text_splitter.split_text(doc))

    # 3. 选择embedding模型（all-MiniLM-L6-v2 轻量且效果不错）
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. 初始化Chroma向量库
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)

    # 5. 添加文本块到向量库
    vector_store.add_texts(chunks)

    # 6. 持久化存储
    vector_store.persist()
    print(f"init over：{persist_dir}")

if __name__ == "__main__":
    # 假设你的文本文件放在当前目录，比如：linyi_report_1.txt、linyi_report_2.txt
    doc_files = ["E:\MSDA-Text\knowledge_base\linyi_report_1.txt"]
    init_linyi_equipment_kb(doc_files)
