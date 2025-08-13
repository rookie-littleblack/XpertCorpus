"""
Micro-ops: remove extra spaces

@author: rookielittleblack
@date:   2025-08-12
"""
import re

from xpertcorpus.utils import xlogger
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


@OPERATOR_REGISTRY.register()
class RemoveExtraSpacesMicroops(OperatorABC):
    def __init__(self):
        xlogger.info(f"Initializing {self.__class__.__name__} ...")
        
        # 代码块检测的正则表达式
        self.code_patterns = [
            # 围栏式代码块（```或~~~开头结尾）
            re.compile(r'```[\s\S]*?```', re.MULTILINE),
            re.compile(r'~~~[\s\S]*?~~~', re.MULTILINE),
            # 缩进代码块（连续4个或以上空格开头的行）
            re.compile(r'^[ \t]{4,}.*$', re.MULTILINE),
            # 行内代码（单反引号包围）
            re.compile(r'`[^`\n]+`'),
            # HTML pre标签
            re.compile(r'<pre[\s\S]*?</pre>', re.IGNORECASE),
            re.compile(r'<code[\s\S]*?</code>', re.IGNORECASE),
            # 常见编程语言的函数定义模式
            re.compile(r'^(def|function|class|public|private|protected)\s+\w+', re.MULTILINE),
            # 包含特殊编程字符的行
            re.compile(r'.*[{}();=><\[\]]+.*', re.MULTILINE),
        ]

    @staticmethod
    def get_desc(lang: str = "zh"):
        return "去除文本中的多余空格和换行符" if lang == "zh" else "Remove extra spaces and newlines in the text."
    
    def _is_likely_code(self, text: str) -> bool:
        """
        检测文本是否可能是代码
        """
        if not text.strip():
            return False
            
        # 检查是否匹配代码模式
        for pattern in self.code_patterns:
            if pattern.search(text):
                return True
        
        # 统计代码特征
        lines = text.split('\n')
        code_indicators = 0
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines == 0:
            return False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查代码特征
            if any([
                # 包含常见编程关键字
                any(keyword in line.lower() for keyword in ['def ', 'function ', 'class ', 'import ', 'from ', 'return ', 'if ', 'else:', 'for ', 'while ', 'try:', 'except:']),
                # 包含赋值操作
                ' = ' in line and not line.startswith('#'),
                # 包含括号和分号
                line.count('(') + line.count(')') >= 2,
                line.endswith(';') or line.endswith('{') or line.endswith('}'),
                # 缩进模式（4个或以上空格）
                line.startswith('    ') and len(line) > 4,
                # 包含特殊字符组合
                '->' in line or '=>' in line or '::' in line,
            ]):
                code_indicators += 1
        
        # 如果超过30%的行具有代码特征，认为是代码
        return (code_indicators / total_lines) > 0.3
    
    def _preserve_code_blocks(self, text: str):
        """
        保护代码块，返回处理后的文本和代码块位置信息
        """
        code_blocks = []
        placeholder_pattern = "___CODE_BLOCK_PLACEHOLDER_{}_END___"
        
        # 提取所有代码块
        for i, pattern in enumerate(self.code_patterns):
            matches = list(pattern.finditer(text))
            for match in reversed(matches):  # 反向处理避免位置偏移
                code_content = match.group()
                placeholder = placeholder_pattern.format(len(code_blocks))
                code_blocks.append(code_content)
                text = text[:match.start()] + placeholder + text[match.end():]
        
        return text, code_blocks, placeholder_pattern
    
    def _restore_code_blocks(self, text: str, code_blocks: list, placeholder_pattern: str):
        """
        恢复代码块
        """
        for i, code_block in enumerate(code_blocks):
            placeholder = placeholder_pattern.format(i)
            text = text.replace(placeholder, code_block)
        return text
    
    def run(self, input_string: str):
        if not input_string:
            return input_string

        try:
            # 保护代码块
            output_string, code_blocks, placeholder_pattern = self._preserve_code_blocks(input_string)
            
            # 1. 移除\r字符
            output_string = output_string.replace("\r", "")
            
            # 2. 处理连续的换行符：3个或以上的换行符替换为2个
            output_string = re.sub(r'\n{3,}', '\n\n', output_string)
            
            # 3. 处理多余的空格（只在非代码区域）
            # 分割文本，逐段处理
            paragraphs = output_string.split('\n\n')
            processed_paragraphs = []
            
            for paragraph in paragraphs:
                if not paragraph.strip():
                    processed_paragraphs.append(paragraph)
                    continue
                    
                # 检查该段落是否可能是代码
                if self._is_likely_code(paragraph):
                    # 是代码，保持原样
                    processed_paragraphs.append(paragraph)
                else:
                    # 不是代码，清理多余空格
                    # 将多个连续空格替换为单个空格
                    lines = paragraph.split('\n')
                    processed_lines = []
                    for line in lines:
                        # 保留行首和行尾，只处理中间的多余空格
                        leading_spaces = len(line) - len(line.lstrip())
                        trailing_spaces = len(line) - len(line.rstrip())
                        content = line.strip()
                        
                        if content:
                            # 将内容中的多个空格替换为单个空格
                            cleaned_content = re.sub(r' {2,}', ' ', content)
                            # 重新组装，保留必要的缩进
                            if leading_spaces > 0:
                                # 保留合理的缩进（最多4个空格）
                                indent = ' ' * min(leading_spaces, 4)
                                processed_line = indent + cleaned_content
                            else:
                                processed_line = cleaned_content
                        else:
                            processed_line = line
                        
                        processed_lines.append(processed_line)
                    
                    processed_paragraphs.append('\n'.join(processed_lines))
            
            output_string = '\n\n'.join(processed_paragraphs)
            
            # 4. 其他文本清理功能
            # 移除行尾的多余空格
            output_string = re.sub(r' +$', '', output_string, flags=re.MULTILINE)
            
            # 清理制表符和空格的混合（标准化为空格）
            output_string = re.sub(r'[ \t]+', lambda m: ' ' if not self._is_likely_code(m.group()) else m.group(), output_string)
            
            # 移除文档开头和结尾的多余空白
            output_string = output_string.strip()
            
            # 恢复代码块
            output_string = self._restore_code_blocks(output_string, code_blocks, placeholder_pattern)
            
            return output_string
            
        except Exception as e:
            xlogger.error(f"Error in removing extra spaces and formatting text: {e}")
            return input_string