from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """从字典中获取指定键的值"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def parse_explanation(explanation):
    """解析名词解释内容，分离不同部分"""
    if not explanation:
        return {}

    # 清理文本，移除多余的符号
    text = explanation.strip()

    # 移除开头和结尾的引号、星号等符号
    text = re.sub(r'^[*"\'`]+|[*"\'`]+$', '', text)

    # 移除所有的#符号
    text = re.sub(r'#+\s*', '', text)

    result = {}

    # 方法1：尝试按 ## 标题分割（最常见的格式）
    sections_found = False
    section_patterns = [
        (r'(?:^|\n)\s*(?:##\s*)?(?:📖\s*)?(?:核心概念|基本概念|概念定义|定义)(?:\s*##)?\s*\n?(.*?)(?=\n\s*(?:##\s*)?(?:📖|🔤|🛠️|💡|🎓)|\Z)', 'core_concept'),
        (r'(?:^|\n)\s*(?:##\s*)?(?:🔤\s*)?(?:术语信息|术语解释|名词解释|基本信息)(?:\s*##)?\s*\n?(.*?)(?=\n\s*(?:##\s*)?(?:📖|🔤|🛠️|💡|🎓)|\Z)', 'term_info'),
        (r'(?:^|\n)\s*(?:##\s*)?(?:🛠️\s*)?(?:工作原理|原理|机制|工作机制)(?:\s*##)?\s*\n?(.*?)(?=\n\s*(?:##\s*)?(?:📖|🔤|🛠️|💡|🎓)|\Z)', 'working_principle'),
        (r'(?:^|\n)\s*(?:##\s*)?(?:💡\s*)?(?:实际应用|应用场景|应用|实践应用)(?:\s*##)?\s*\n?(.*?)(?=\n\s*(?:##\s*)?(?:📖|🔤|🛠️|💡|🎓)|\Z)', 'practical_application'),
        (r'(?:^|\n)\s*(?:##\s*)?(?:🎓\s*)?(?:学习要点|要点|关键点|重点)(?:\s*##)?\s*\n?(.*?)(?=\n\s*(?:##\s*)?(?:📖|🔤|🛠️|💡|🎓)|\Z)', 'learning_points')
    ]

    for pattern, section_key in section_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if content:
                # 清理内容
                content = re.sub(r'\n+', '\n', content)  # 合并多个换行
                content = re.sub(r'^\s*[-*•]\s*', '', content, flags=re.MULTILINE)  # 移除列表符号
                content = re.sub(r'^\s*\d+\.\s*', '', content, flags=re.MULTILINE)  # 移除数字列表
                result[section_key] = content
                sections_found = True

    # 方法2：如果没有找到结构化内容，尝试按emoji图标分割
    if not sections_found:
        emoji_patterns = [
            (r'📖\s*[^📖🔤🛠️💡🎓]*', 'core_concept'),
            (r'🔤\s*[^📖🔤🛠️💡🎓]*', 'term_info'),
            (r'🛠️\s*[^📖🔤🛠️💡🎓]*', 'working_principle'),
            (r'💡\s*[^📖🔤🛠️💡🎓]*', 'practical_application'),
            (r'🎓\s*[^📖🔤🛠️💡🎓]*', 'learning_points')
        ]

        for pattern, section_key in emoji_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(0)
                # 移除emoji和清理内容
                content = re.sub(r'^[📖🔤🛠️💡🎓]\s*', '', content)
                content = content.strip()
                if content:
                    result[section_key] = content
                    sections_found = True

    # 方法3：如果还是没有找到结构化内容，尝试简单分段
    if not sections_found:
        # 按双换行分段
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) >= 2:
            result['core_concept'] = paragraphs[0]
            if len(paragraphs) >= 2:
                result['term_info'] = paragraphs[1] if len(paragraphs) > 2 else ''
            if len(paragraphs) >= 3:
                result['working_principle'] = paragraphs[2] if len(paragraphs) > 3 else ''
            if len(paragraphs) >= 4:
                result['practical_application'] = paragraphs[3] if len(paragraphs) > 4 else ''
            if len(paragraphs) >= 5:
                result['learning_points'] = paragraphs[4]
        elif len(paragraphs) == 1:
            # 如果只有一段，尝试按句号分割
            sentences = [s.strip() for s in paragraphs[0].split('。') if s.strip()]
            if len(sentences) >= 2:
                result['core_concept'] = sentences[0] + '。'
                result['practical_application'] = '。'.join(sentences[1:]) + '。'
            else:
                result['core_concept'] = paragraphs[0]

    # 如果还是没有内容，使用原始文本
    if not result:
        result['core_concept'] = text

    return result

@register.filter
def clean_text(text):
    """清理文本中的多余符号"""
    if not text:
        return ''

    # 移除多余的星号、引号等
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'^["\']|["\']$', '', text)

    # 移除所有的#符号
    text = re.sub(r'#+\s*', '', text)

    # 移除emoji后面的空格
    text = re.sub(r'[📖🔤🛠️💡🎓]\s*', '', text)

    # 清理多余的换行和空格
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)

    # 移除开头的数字编号
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)

    return text.strip()
