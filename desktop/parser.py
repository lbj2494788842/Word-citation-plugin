"""
引用解析模块
从用户粘贴的文本中提取 [N] 格式的参考文献条目
"""

import re


class ParsedCitation:
    """解析后的单条引用"""

    def __init__(self, id: int, text: str, original_text: str):
        self.id = id
        self.text = text          # 去除 [N] 前缀后的纯文本
        self.original_text = original_text  # 原始文本


def parse_citations(input_text: str) -> list[ParsedCitation]:
    """
    解析用户输入的参考文献文本

    支持两种格式：
      1. 明确的 [N] 前缀（如 [1] 作者. 标题...）
      2. 每行一条，自动编号
    """
    result: list[ParsedCitation] = []
    cleaned = input_text.strip()

    if not cleaned:
        return result

    # 尝试匹配 [N] 前缀格式
    citation_regex = r'\[(\d+)\]([^\[]*(?:\[[^\d][^\[]*\][^\[]*)*)'
    matches = list(re.finditer(citation_regex, cleaned))

    if matches:
        for match in matches:
            id_val = int(match.group(1))
            text = match.group(2).strip()
            if text:
                result.append(ParsedCitation(id_val, text, f'[{id_val}]{text}'))
    else:
        # 兜底：按行分割，自动编号
        lines = [l.strip() for l in cleaned.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            cleaned_text = re.sub(r'^\[\d+\]\s*', '', line).strip()
            if cleaned_text:
                result.append(ParsedCitation(i + 1, cleaned_text, line))

    result.sort(key=lambda x: x.id)
    return result
