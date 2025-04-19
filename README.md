# AuraLingua: 多阶段翻译

## 项目简介

AuraLingua 是一个基于 Gradio 框架构建的多阶段翻译应用，旨在提供一个可视化界面，用户可以方便地利用大型语言模型（LLM）进行自动化、分阶段的翻译流程。应用支持通过 `.env` 文件灵活配置不同的 LLM API，并内置 Prompt 编辑器，允许用户根据需求定制各翻译阶段的 Prompt。

## 主要特性

*   **四轮接力翻译流程:** 自动化执行以下步骤：专有名词识别 -> 直接翻译 -> 问题识别 -> 意译。
*   **可视化用户界面:** 基于 Gradio 提供的简洁易用的交互界面。
*   **可配置的 LLM API:** 通过 `.env` 文件轻松切换和配置 OpenAI 或兼容 API 的 Base URL, API Key 和模型。
*   **内置 Prompt 编辑器:** 直接在应用界面中查看、编辑和保存各翻译阶段的 Prompt。
*   **模块化后端设计:** 翻译逻辑封装在独立的 Service 类中，提高了代码的可维护性和可扩展性。
*   **详细日志记录:** 记录应用运行过程中的关键信息和错误，便于监控和调试，日志同时输出到控制台和文件。

## 文件结构

```
AuraLingua/
├── app.py                 # Gradio 应用主文件
├── backend/               # 后端逻辑目录
│   ├── services/          # 业务逻辑服务模块
│   │   └── translation_service.py # 翻译服务类 (包含 Base, ProperNouns, StraightUp, Issue, Loose)
│   ├── prompts/           # Prompt 文本文件存放目录
│   │   ├── issue_spotting_prompt.txt
│   │   ├── loose_translation_prompt.txt
│   │   ├── proper_nouns_spotting_prompt.txt
│   │   └── straight_up_translation_prompt.txt
│   ├── logs/              # 日志文件目录 (运行时生成)
│   │   └── app.log
│   ├── config.py          # 应用配置 (日志、Prompt 加载、API 配置)
│   └── __init__.py        # 使 backend 成为 Python 包
├── tests/                 # 测试文件目录 (可选)
├── .env                   # 环境变量配置文件 (需手动创建和配置)
├── README.md              # 项目说明文件
└── requirements.txt       # 项目依赖文件
```

## 快速开始

### 环境要求

*   Python 3.10+
*   访问 OpenAI (或兼容) API 的权限及 API Key。

### 安装步骤

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/ID-VerNe/AuraLingua.git
    cd AuraLingua
    ```
    

2.  **创建并激活虚拟环境 (推荐):**
    ```bash
    # macOS/Linux
    python -m venv .venv
    source .venv/bin/activate

    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **安装项目依赖:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置 LLM API:**
    在项目根目录下手动创建一个名为 `.env` 的文件，并添加以下内容（请替换为你的实际 API 配置信息）：
    ```env
    OPENAI_API_BASE=https://api.openai.com/v1  # 或你的自定义 API Base URL
    OPENAI_API_KEY=YOUR_ACTUAL_API_KEY         # 替换为你的 API Key
    OPENAI_MODEL=gpt-3.5-turbo                # 或你希望使用的模型，如 gpt-4, gemini-2.0-flash-thinking-exp-01-21 等
    ```
    

### 运行应用

确保你已经按照上述步骤安装了依赖并配置了 `.env` 文件。在虚拟环境激活状态下，运行：

```bash
python app.py
```

应用成功启动后，控制台将输出 Gradio 应用的本地访问地址（通常是 `http://127.0.0.1:7860/`）。在浏览器中打开该地址即可使用应用。

## 使用指南

应用界面包含两个 Tab 页：

1.  **Prompt 编辑器:**
    *   通过下拉菜单选择需要查看或编辑的 Prompt。
    *   在文本区域修改 Prompt 内容。
    *   点击 "保存 Prompt" 按钮将修改保存到对应的 `.txt` 文件，并同步更新内存中的 Prompt，下次翻译将使用修改后的 Prompt。

2.  **接力翻译:**
    *   在 "英文原文" 文本框中输入需要翻译的英文文本。
    *   依次点击四个步骤按钮：
        *   "1. 识别专有名词": 提取并显示技术术语列表。
        *   "2. 进行直接翻译": 基于原文和专有名词（已自动传递）进行直接翻译。
        *   "3. 识别翻译问题": 基于直接翻译结果、原文和专有名词，分析并指出翻译中可能存在的问题。
        *   "4. 进行意译": 基于直接翻译结果、问题识别结果、原文和专有名词，进行更符合中文习惯的意译。
    *   每个步骤的结果将显示在对应的输出框中。输出框设置为可编辑，方便用户查看和临时修改（*请注意，目前的修改仅影响显示，不影响后续步骤的计算，如需实现影响下游的编辑功能，需要进一步开发*）。

## 代码架构与日志

项目代码遵循模块化和分层设计原则。后端逻辑位于 `backend/` 目录，Services 层封装了与 LLM 交互及 Prompt 处理的业务逻辑。

应用集成了详细的日志记录功能，日志信息同时输出到控制台和 `backend/logs/app.log` 文件，记录了应用启动、Prompt 加载、API 调用等关键事件，便于开发者调试和监控应用运行状态。

## 未来可能的增强

*   实现用户对中间翻译结果的编辑并影响后续步骤计算的功能。
*   增加对更多 LLM 提供商（如 Google Gemini, Anthropic Claude 等）的支持。
*   优化界面布局和样式，提升用户体验。
*   添加用户认证和权限管理功能。
*   支持上传文件进行批量翻译。

## 贡献

欢迎对本项目提出改进意见或贡献代码。请提交 Issue 或 Pull Request。