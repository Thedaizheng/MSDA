import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    assert os.getenv("DEEPSEEK_API_KEY"), "DEEPSEEK_API_KEY 未设置"
