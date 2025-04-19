# backend/services/translation_service.py
import logging
import openai
from backend.config import PROPER_NOUNS_SPOTTING_PROMPT, STRAIGHT_UP_TRANSLATION_PROMPT, ISSUE_SPOTTING_PROMPT, LOOSE_TRANSLATION_PROMPT # 导入所有 prompt 变量
from backend.config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL

logger = logging.getLogger(__name__)

class BaseTranslationService: # 创建 BaseTranslationService 基类
    """翻译服务的基类，封装通用功能."""
    def __init__(self, prompt):
        """
        构造函数.

        Args:
            prompt (str):  当前服务需要使用的 Prompt 内容.
        """
        self.prompt = prompt # 加载 prompt (由子类传入具体的 prompt)
        self.api_key = OPENAI_API_KEY
        self.api_base = OPENAI_API_BASE
        self.model = OPENAI_MODEL

        if not self.api_key:
            logger.error("OPENAI_API_KEY is not configured. OpenAI API calls will fail.")
        logger.info(f"{self.__class__.__name__} 初始化，API Base: {self.api_base}, Model: {self.model}") # 使用 __class__.__name__ 获取子类类名
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base if self.api_base else "https://api.openai.com/v1"
        )

    def _run_api_call(self, constructed_prompt): # 定义通用的 _run_api_call 方法 (protected 方法)
        """
        封装 OpenAI API 调用的通用逻辑.

        Args:
            constructed_prompt (str):  构建好的完整 Prompt.

        Returns:
            str:  LLM 返回的文本结果.
            str:  如果 API 调用出错，返回错误信息字符串.
        """
        logger.debug(f"Constructed prompt for OpenAI API:\n{constructed_prompt}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": constructed_prompt}
                ]
            )
            llm_result = response.choices[0].message.content
            logger.debug(f"Raw LLM response: {llm_result}")
            return llm_result
        except Exception as e:
            logger.error(f"Error calling OpenAI API from {self.__class__.__name__}: {e}", exc_info=True) # 在日志中包含类名
            return f"Error calling OpenAI API: {e}"

    def run_prompt(self, origin_text, **kwargs): # 基类的 run_prompt 方法 (模板方法)
        """
        运行 Prompt 的模板方法，子类需要Override 此方法实现具体的 Prompt 处理逻辑.
        """
        raise NotImplementedError("run_prompt 方法需要在子类中被Override 实现") # 抛出 NotImplementedError 异常，强制子类实现

class ProperNounsSpottingService(BaseTranslationService): # ProperNounsSpottingService 继承自 BaseTranslationService
    def __init__(self):
        super().__init__(PROPER_NOUNS_SPOTTING_PROMPT) # 调用父类构造函数，并传入 Proper Nouns Spotting Prompt

    def run_prompt(self, origin_text): # 实现子类特有的 run_prompt 方法
        """
        运行 Proper Nouns Spotting Prompt，调用 OpenAI API.
        """
        logger.info("Running Proper Nouns Spotting Prompt with OpenAI API...")
        logger.debug(f"Origin text: {origin_text}")

        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set. Cannot call OpenAI API.")
            return "Error: OpenAI API Key is not configured. Please set OPENAI_API_KEY environment variable or in .env file."

        constructed_prompt = self.prompt.replace("{{origin_text}}", origin_text) # 构建特定于 Proper Nouns Spotting 的 Prompt
        llm_result = self._run_api_call(constructed_prompt) # 复用基类的 _run_api_call 方法

        return llm_result # 直接返回 LLM 结果 (假设 LLM 返回 Markdown 表格)

class StraightUpTranslationService(BaseTranslationService): # StraightUpTranslationService 继承自 BaseTranslationService
    def __init__(self):
        super().__init__(STRAIGHT_UP_TRANSLATION_PROMPT) # 调用父类构造函数，并传入 Straight-up Translation Prompt

    def run_prompt(self, origin_text, proper_nouns_table=""): # 实现子类特有的 run_prompt 方法
        """
        运行 Straight-up Translation Prompt, 调用 OpenAI API 进行直接翻译.
        """
        logger.info("Running Straight-up Translation Prompt with OpenAI API...")
        logger.debug(f"Origin text: {origin_text}")
        logger.debug(f"Proper nouns table:\n{proper_nouns_table}")

        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set. Cannot call OpenAI API.")
            return "Error: OpenAI API Key is not configured. Please set OPENAI_API_KEY environment variable or in .env file."

        constructed_prompt = self.prompt.replace("{{origin_text}}", origin_text) # 构建特定于 Straight-up Translation 的 Prompt
        constructed_prompt = constructed_prompt.replace("{{proper_nouns}}", proper_nouns_table)
        llm_result = self._run_api_call(constructed_prompt) # 复用基类的 _run_api_call 方法

        return llm_result # 直接返回 LLM 结果 (假设 LLM 返回 纯文本)

class IssueSpottingService(BaseTranslationService): # IssueSpottingService 继承自 BaseTranslationService
    def __init__(self):
        super().__init__(ISSUE_SPOTTING_PROMPT) # 调用父类构造函数，并传入 Issue Spotting Prompt

    def run_prompt(self, straight_up, origin_text, proper_nouns): # 实现子类特有的 run_prompt 方法，接收三个参数
        """
        运行 Issue Spotting Prompt,  指出直接翻译存在的问题。

        Args:
            straight_up (str): 直接翻译的结果
            origin_text (str): 原始英文文本
            proper_nouns (str): 专有名词表格 (Markdown 格式字符串)

        Returns:
            str:  LLM 返回的 润色后的文本 结果.
        """
        logger.info("Running Issue Spotting Prompt with OpenAI API...")
        logger.debug(f"Straight up translation: {straight_up}")
        logger.debug(f"Origin text: {origin_text}")
        logger.debug(f"Proper nouns: {proper_nouns}")

        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set. Cannot call OpenAI API.")
            return "Error: OpenAI API Key is not configured. Please set OPENAI_API_KEY environment variable or in .env file."

        constructed_prompt = self.prompt.replace("{{straight_up}}", straight_up) # 构建特定于 Issue Spotting 的 Prompt
        constructed_prompt = constructed_prompt.replace("{{origin_text}}", origin_text)
        constructed_prompt = constructed_prompt.replace("{{proper_nouns}}", proper_nouns)

        llm_result = self._run_api_call(constructed_prompt) # 复用基类的 _run_api_call 方法
        return llm_result

class LooseTranslationService(BaseTranslationService): # LooseTranslationService 继承自 BaseTranslationService
    def __init__(self):
        super().__init__(LOOSE_TRANSLATION_PROMPT) # 调用父类构造函数，并传入 Loose Translation Prompt

    def run_prompt(self, straight_up, issue_spotting_result, origin_text, proper_nouns): # 修改 run_prompt 方法，移除 last_translation_text 参数
        """
        运行 Loose Translation Prompt,  进行意译，更准确传达原文含义。

        Args:
            straight_up (str): 直接翻译的结果
            issue_spotting_result (str): 问题识别结果
            origin_text (str): 原始英文文本
            proper_nouns (str): 专有名词表格 (Markdown 格式字符串)

        Returns:
            str:  LLM 返回的 意译 结果.
        """
        logger.info("Running Loose Translation Prompt with OpenAI API...")
        logger.debug(f"Straight up translation: {straight_up}")
        logger.debug(f"Issue spotting result: {issue_spotting_result}")
        logger.debug(f"Origin text: {origin_text}")
        logger.debug(f"Proper nouns: {proper_nouns}")

        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set. Cannot call OpenAI API.")
            return "Error: OpenAI API Key is not configured. Please set OPENAI_API_KEY environment variable or in .env file."

        constructed_prompt = self.prompt.replace("{{straight_up}}", straight_up) # 构建特定于 Loose Translation 的 Prompt
        constructed_prompt = constructed_prompt.replace("{{issue}}", issue_spotting_result) # 使用 issue_spotting_result，变量名更清晰
        constructed_prompt = constructed_prompt.replace("{{origin_text}}", origin_text)
        constructed_prompt = constructed_prompt.replace("{{proper_nouns}}", proper_nouns)

        llm_result = self._run_api_call(constructed_prompt) # 复用基类的 _run_api_call 方法
        return llm_result

if __name__ == '__main__':
    # 单元测试 (可选)
    proper_nouns_service = ProperNounsSpottingService()
    test_text_nouns = "Prompt Engineering and Text Generation are related to Token and Prompt, diffusion models and Transformer."
    result_nouns = proper_nouns_service.run_prompt(test_text_nouns)
    print("Test Result (Proper Nouns Spotting, OpenAI API):\n", result_nouns)

    straight_translation_service = StraightUpTranslationService()
    test_text_translation = "This is a test sentence for straight-up translation."
    test_proper_nouns_table = """
| 英文 | 中文 |
|---|---|
| Test | 测试 |
| Sentence | 句子 |
"""
    result_translation = straight_translation_service.run_prompt(test_text_translation, test_proper_nouns_table)
    print("\nTest Result (Straight-up Translation, OpenAI API):\n", result_translation)

    issue_spotting_service = IssueSpottingService()
    test_straight_up_translation = "这是一个直接翻译的测试句子。"
    test_origin_text_issue = "This is a test sentence for issue spotting."
    test_proper_nouns_issue = """
| 英文 | 中文 |
|---|---|
| Issue Spotting | 问题识别 |
"""
    result_issue = issue_spotting_service.run_prompt(test_straight_up_translation, test_origin_text_issue, test_proper_nouns_issue)
    print("\nTest Result (Issue Spotting, OpenAI API):\n", result_issue)

    loose_translation_service = LooseTranslationService()
    test_last_translation_loose = "前一轮翻译结果"
    test_straight_up_loose = "直接翻译结果"
    test_issue_loose = "翻译问题描述"
    test_origin_text_loose = "This is a test sentence for loose translation."
    test_proper_nouns_loose = """
| 英文 | 中文 |
|---|---|
| Loose Translation | 意译 |
"""
    result_loose = loose_translation_service.run_prompt(test_last_translation_loose, test_straight_up_loose, test_issue_loose, test_origin_text_loose, test_proper_nouns_loose)
    print("\nTest Result (Loose Translation, OpenAI API):\n", result_loose)