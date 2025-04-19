# backend/config.py
import logging
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

def setup_logging():
    """配置日志记录."""
    log_dir = 'backend/logs'
    os.makedirs(log_dir, exist_ok=True) # 确保日志目录存在
    log_filename = os.path.join(log_dir, 'app.log')

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO, # 默认日志级别为 INFO，可以根据需要调整
        format='[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8'
    )
    console_handler = logging.StreamHandler() # 创建控制台处理器
    console_handler.setLevel(logging.INFO) # 控制台日志级别
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler) # 将控制台处理器添加到根logger

    logger = logging.getLogger(__name__)
    logger.info("日志系统已配置.") # 记录日志系统启动信息

# 定义 prompt 文件路径
PROMPT_DIR = 'backend/prompts'
PROPER_NOUNS_SPOTTING_PROMPT_FILE = os.path.join(PROMPT_DIR, 'proper_nouns_spotting_prompt.txt')
STRAIGHT_UP_TRANSLATION_PROMPT_FILE = os.path.join(PROMPT_DIR, 'straight_up_translation_prompt.txt')
ISSUE_SPOTTING_PROMPT_FILE = os.path.join(PROMPT_DIR, 'issue_spotting_prompt.txt')
LOOSE_TRANSLATION_PROMPT_FILE = os.path.join(PROMPT_DIR, 'loose_translation_prompt.txt')

# 加载 prompt 内容到变量
def load_prompt(prompt_file):
    """加载 prompt 文件内容."""
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {prompt_file}")
        return ""
    except Exception as e:
        logging.error(f"Error reading prompt file: {prompt_file}, error: {e}")
        return ""

PROPER_NOUNS_SPOTTING_PROMPT = load_prompt(PROPER_NOUNS_SPOTTING_PROMPT_FILE)
STRAIGHT_UP_TRANSLATION_PROMPT = load_prompt(STRAIGHT_UP_TRANSLATION_PROMPT_FILE)
ISSUE_SPOTTING_PROMPT = load_prompt(ISSUE_SPOTTING_PROMPT_FILE)
LOOSE_TRANSLATION_PROMPT = load_prompt(LOOSE_TRANSLATION_PROMPT_FILE)

# OpenAI API 配置
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE") # 从环境变量或 .env 文件中读取 OPENAI_API_BASE
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # 从环境变量或 .env 文件中读取 OPENAI_API_KEY
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo") # 从环境变量或 .env 文件中读取 OPENAI_MODEL, 默认 "gpt-3.5-turbo"

if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY 环境变量或 .env 文件中未设置，请先设置 OPENAI_API_KEY 才能使用 OpenAI API 功能。")
if not OPENAI_API_BASE:
    logging.warning("OPENAI_API_BASE 环境变量或 .env 文件中未设置，将使用默认 OpenAI API Base (https://api.openai.com/v1)。")
if not OPENAI_MODEL:
    logging.info(f"OPENAI_MODEL 环境变量或 .env 文件中未设置，将使用默认模型: gpt-3.5-turbo。")

if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("这是一条来自 config.py 的测试日志信息")

    # 打印加载的 prompt (测试用)
    print("PROPER_NOUNS_SPOTTING_PROMPT:\n", PROPER_NOUNS_SPOTTING_PROMPT)
    print("\nSTRAIGHT_UP_TRANSLATION_PROMPT:\n", STRAIGHT_UP_TRANSLATION_PROMPT)
    print("\nISSUE_SPOTTING_PROMPT:\n", ISSUE_SPOTTING_PROMPT)
    print("\nLOOSE_TRANSLATION_PROMPT:\n", LOOSE_TRANSLATION_PROMPT)

    print("\nOPENAI_API_BASE:", OPENAI_API_BASE) # 打印 OpenAI API 配置 (测试用)
    print("OPENAI_API_KEY:", OPENAI_API_KEY)
    print("OPENAI_MODEL:", OPENAI_MODEL)