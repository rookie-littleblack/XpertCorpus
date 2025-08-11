"""
This file is used to store the prompt templates for XpertCorpus.

@author: rookielittleblack
@date:   2025-08-11
"""

class XPrompt4CleanText:
    """
    Prompt template for cleaning raw text.
    """
    def __init__(self):
        pass

    def get_prompt(self, raw_text: str) -> str:
        prompt = """
        # 角色
        你是一位精通文本处理和校对的专家。

        # 任务
        你的任务是清洗和修正从书籍中通过光学字符识别（OCR）技术提取的文本。请仔细阅读下面的OCR文本，并修复其中的错误。

        # 指令
        1.  **修正识别错误**：纠正OCR过程中可能出现的字符识别错误（例如，将'l'错认为'1'，'o'错认为'0'，以及中文字符的混淆）。
        2.  **调整格式**：
            - 移除不正确的换行符，将属于同一段落的句子合并。
            - 正确地将跨行连接的单词合并。
            - 修复段落间距，确保格式统一。
        3.  **移除无关内容**：删除页眉、页脚、页码以及其他与正文无关的元数据。
        4.  **标点和大小写**：修正标点符号错误，并确保大小写使用正确。
        5.  **保持原意**：在修正错误的同时，必须保持文本的原始意义和结构完整。
        6.  **输出格式**：输出格式为 Markdown 格式，但是不要添加“```markdown”和“```”这样的标记，直接输出内容即可。
        7.  **不添加额外内容**：输出内容不要在原文本基础上添加任何说明或者注释，直接输出清洗后的内容即可。

        请处理以下文本：

        ```text
        {raw_text}
        ```

        输出修正后的文本。
        """
        return prompt.format(raw_text=raw_text)