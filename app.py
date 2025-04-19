# app.py
import gradio as gr
import logging
from backend.config import setup_logging, PROMPT_DIR, PROPER_NOUNS_SPOTTING_PROMPT_FILE, STRAIGHT_UP_TRANSLATION_PROMPT_FILE, ISSUE_SPOTTING_PROMPT_FILE, LOOSE_TRANSLATION_PROMPT_FILE
from backend.config import PROPER_NOUNS_SPOTTING_PROMPT, STRAIGHT_UP_TRANSLATION_PROMPT, ISSUE_SPOTTING_PROMPT, LOOSE_TRANSLATION_PROMPT
# 确保导入了所有需要的 Service 类
from backend.services.translation_service import ProperNounsSpottingService, StraightUpTranslationService, IssueSpottingService, LooseTranslationService

# 初始化日志
setup_logging()
logger = logging.getLogger(__name__)

# 定义 prompt 文件路径和对应的变量名的字典，方便后续操作
PROMPT_FILES = {
    "Proper Nouns Spotting": PROPER_NOUNS_SPOTTING_PROMPT_FILE,
    "Straight-up Translation": STRAIGHT_UP_TRANSLATION_PROMPT_FILE,
    "Issue Spotting": ISSUE_SPOTTING_PROMPT_FILE,
    "Loose Translation": LOOSE_TRANSLATION_PROMPT_FILE,
}

# 加载 prompt 内容到变量 - 这一步依然需要在程序启动时完成
# 注意：这里直接从 backend.config 导入了加载好的 PROMPT 变量
# 如果在 Prompt 编辑器中修改后，需要确保这个修改能反映到实际的服务调用中
# 我们当前的实现是通过更新内存中的 PROMPTS 字典，并在 Service.__init__ 中加载
# 如果 Service 是在每次调用时创建新实例，那么它们会加载最新的 PROMPT 内容
PROMPTS = {
    "Proper Nouns Spotting": PROPER_NOUNS_SPOTTING_PROMPT,
    "Straight-up Translation": STRAIGHT_UP_TRANSLATION_PROMPT,
    "Issue Spotting": ISSUE_SPOTTING_PROMPT,
    "Loose Translation": LOOSE_TRANSLATION_PROMPT,
}

def display_prompt(prompt_name):
    """根据 prompt 名称返回 prompt 内容."""
    logger.info(f"Displaying prompt: {prompt_name}")
    # 从内存中的实时 PROMPTS 字典获取 Prompt 内容，这样能反映编辑器的修改
    return PROMPTS.get(prompt_name, "Prompt not found")

def save_prompt(prompt_name, prompt_content):
    """保存 prompt 内容到文件，并更新内存中的字典."""
    logger.info(f"Saving prompt: {prompt_name}")
    prompt_file = PROMPT_FILES.get(prompt_name)
    if not prompt_file:
        logger.warning(f"Prompt file not found for prompt name: {prompt_name}")
        return "Error: Prompt name not found."

    try:
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        # 更新内存中的 PROMPTS 字典，这是关键
        PROMPTS[prompt_name] = prompt_content
        logger.info(f"Prompt '{prompt_name}' saved to '{prompt_file}' successfully.")
        return "Prompt saved successfully!"
    except Exception as e:
        logger.error(f"Error saving prompt '{prompt_name}' to '{prompt_file}': {e}", exc_info=True)
        return f"Error saving prompt: {e}"

# --- 接力翻译步骤函数 ---

# 注意：这些函数在每次按钮点击时都会被调用，并创建 Service 实例
# Service 实例会在 __init__ 中加载 Prompt。
# 如果希望 Service 实例在应用启动时只创建一次，或者需要更复杂的依赖注入，
# 可以调整 app 结构，例如将 Service 实例作为参数传递，或者使用全局变量。
# 但目前这种方式对于 Gradio 应用来说，简单且便于 State 管理。

def run_proper_nouns_spotting_step(origin_text):
    """执行专有名词识别步骤."""
    logger.info("Starting Proper Nouns Spotting step...")
    service = ProperNounsSpottingService()
    # run_prompt 方法现在应该只返回一个值 (表格 markdown)
    result_table_markdown = service.run_prompt(origin_text)
    logger.info("Proper Nouns Spotting step completed.")
    # 返回结果用于更新输出框和 State
    return result_table_markdown, result_table_markdown

def run_straight_up_translation_step(origin_text, proper_nouns_table):
    """执行直接翻译步骤."""
    logger.info("Starting Straight-up Translation step...")
    service = StraightUpTranslationService()
    # run_prompt 方法现在应该只返回一个值 (翻译文本)
    result_text = service.run_prompt(origin_text, proper_nouns_table)
    logger.info("Straight-up Translation step completed.")
    # 返回结果用于更新 State
    return result_text

# 纠正 Issue Spotting 函数，使其只更新一个 State
def run_issue_spotting_step(straight_up_translation_text, origin_text, proper_nouns_table):
    """执行问题识别步骤."""
    logger.info("Starting Issue Spotting step...")
    service = IssueSpottingService()
    # IssueSpottingService.run_prompt 应该返回一个值 (问题描述文本)
    result_text = service.run_prompt(straight_up_translation_text, origin_text, proper_nouns_table)
    logger.info("Issue Spotting step completed.")
    # 返回结果用于更新 State
    return result_text

# 纠正 Loose Translation 函数签名和调用
def run_loose_translation_step(straight_up_translation_text, issue_spotting_result_text, origin_text, proper_nouns_table):
    """执行意译步骤."""
    logger.info("Starting Loose Translation step...")
    service = LooseTranslationService()
    # LooseTranslationService.run_prompt 应该接收修改后的参数
    result_text = service.run_prompt(straight_up_translation_text, issue_spotting_result_text, origin_text, proper_nouns_table)
    logger.info("Loose Translation step completed.")
    # 返回结果用于更新 State
    return result_text

if __name__ == "__main__":
    logger.info("Starting Gradio application...")

    prompt_names = list(PROMPTS.keys())
    with gr.Blocks(title="Translation App") as iface:
        gr.Markdown("# 翻译流程")

        # 初始化 gr.State 组件，存储各个步骤的结果
        # 这些 State 将在各个按钮点击事件的 outputs 中被隐式更新
        stored_proper_nouns_table = gr.State("")
        stored_straight_up_translation_text = gr.State("")
        stored_issue_spotting_result_text = gr.State("")
        stored_final_translation_text = gr.State("") # 存储最终意译结果

        with gr.Tab("翻译流程"):
            gr.Markdown("## 翻译流程")

            # 英文原文输入框 (所有步骤共用)
            origin_text_input_relay = gr.TextArea(label="英文原文", lines=5)

            with gr.Row():
                # 设置按钮宽度比例和点击事件
                spot_nouns_button_relay = gr.Button("1. 识别专有名词", scale=1)
                straight_translate_button_relay = gr.Button("2. 进行直接翻译", scale=1)
                spot_issues_button_relay = gr.Button("3. 识别翻译问题", scale=1)
                loose_translate_button_relay = gr.Button("4. 进行意译", scale=1)

            # 四个结果输出框，使用 Row 排列
            with gr.Row():
                proper_nouns_output_relay = gr.TextArea(label="步骤1：专有名词识别结果", interactive=True, lines=10,
                                                        scale=1)  # scale 控制宽度比例
                straight_up_translation_output_relay = gr.TextArea(label="步骤2：直接翻译结果", interactive=True,
                                                                   lines=10, scale=1)
            with gr.Row():
                issue_spotting_output_relay = gr.TextArea(label="步骤3：问题识别结果", interactive=True, lines=10,
                                                          scale=1)
                loose_translation_output_relay = gr.TextArea(label="步骤4：意译结果", interactive=True, lines=10,
                                                             scale=1)

            # 四个步骤按钮，使用 Row 排列

            # 按钮点击事件配置: 触发函数，输入由哪些组件提供，输出更新哪些组件或 State

            # 步骤 1: 识别专有名词
            spot_nouns_button_relay.click(
                fn=run_proper_nouns_spotting_step,  # 调用对应的步骤函数
                inputs=origin_text_input_relay,  # 输入是英文原文
                # 输出更新专有名词输出Markdown，以及存储专有名词的State
                outputs=[proper_nouns_output_relay, stored_proper_nouns_table]
            )

            # 步骤 2: 进行直接翻译 (依赖于英文原文和专有名词State)
            straight_translate_button_relay.click(
                fn=run_straight_up_translation_step,
                inputs=[origin_text_input_relay, stored_proper_nouns_table],  # 输入：英文原文，存储的专有名词State
                outputs=stored_straight_up_translation_text  # 输出更新存储直接翻译的State
            )

            # 步骤 3: 识别翻译问题 (依赖于直接翻译State，英文原文，专有名词State)
            spot_issues_button_relay.click(
                fn=run_issue_spotting_step,
                inputs=[stored_straight_up_translation_text, origin_text_input_relay, stored_proper_nouns_table],
                # 输入：存储的直接翻译State，英文原文，存储的专有名词State
                outputs=stored_issue_spotting_result_text  # 输出更新存储问题识别结果的State
            )

            # 步骤 4: 进行意译 (依赖于直接翻译State, 问题识别State, 英文原文, 专有名词State)
            loose_translate_button_relay.click(
                fn=run_loose_translation_step,
                inputs=[stored_straight_up_translation_text, stored_issue_spotting_result_text, origin_text_input_relay,
                        stored_proper_nouns_table],  # 输入：存储的直接翻译State, 存储的问题识别State, 英文原文, 存储的专有名词State
                outputs=stored_final_translation_text  # 输出更新存储最终意译结果的State
            )

            # State 组件 change 事件：当 State 更新时，自动将 State 的值赋给对应的输出文本框
            # gradio 会自动处理 State 的 change 事件，只要它在某个 fn 的 outputs 列表中
            # 当 State 的值发生变化时，其 change 事件会被触发
            # 我们需要注册 change 事件来更新对应的 Textbox/Markdown
            stored_proper_nouns_table.change(
                fn=lambda x: x,  # lambda 函数直接返回输入值
                inputs=stored_proper_nouns_table,  # change 事件的输入就是自身 State 的新值
                outputs=proper_nouns_output_relay  # 更新专有名词显示框
            )

            stored_straight_up_translation_text.change(
                fn=lambda x: x,
                inputs=stored_straight_up_translation_text,
                outputs=straight_up_translation_output_relay  # 更新直接翻译显示框
            )

            stored_issue_spotting_result_text.change(
                fn=lambda x: x,
                inputs=stored_issue_spotting_result_text,
                outputs=issue_spotting_output_relay  # 更新问题识别显示框
            )

            stored_final_translation_text.change(
                fn=lambda x: x,
                inputs=stored_final_translation_text,
                outputs=loose_translation_output_relay  # 更新意译显示框
            )


        with gr.Tab("Prompt 编辑器"):
            gr.Markdown("## Prompt 编辑器") # 添加二级标题
            prompt_selector = gr.Dropdown(prompt_names, label="选择 Prompt")
            prompt_textarea = gr.TextArea(
                value=display_prompt(prompt_names[0]) if prompt_names else "",
                label="Prompt 内容",
                lines=10 # 设置文本框行数
            )
            save_button = gr.Button("保存 Prompt")

            prompt_selector.change(
                fn=display_prompt,
                inputs=prompt_selector,
                outputs=prompt_textarea
            )
            save_button.click(
                fn=save_prompt,
                inputs=[prompt_selector, prompt_textarea],
                outputs=gr.Text(label="保存状态")
            )



    iface.launch()
    logger.info("Gradio application started.")