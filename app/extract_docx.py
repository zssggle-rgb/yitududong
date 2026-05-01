"""
DOCX 文本抽取模块 - M01
使用 python-docx 从 Word 文档中抽取结构化文本。
"""
from docx import Document


def extract_text_from_docx(filepath: str) -> str:
    """从 DOCX 文件中提取所有文本"""
    doc = Document(filepath)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_structured_from_docx(filepath: str) -> dict:
    """
    从 DOCX 中提取结构化内容。
    返回 dict: title, subtitle, paragraphs, key_points, source
    """
    full_text = extract_text_from_docx(filepath)
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
    
    if not lines:
        return {
            "title": "",
            "subtitle": "",
            "paragraphs": [],
            "key_points": [],
            "source": "",
            "full_text": ""
        }
    
    # 标题为第一行
    title = lines[0]
    subtitle = lines[1] if len(lines) > 1 else ""
    
    # 段落
    paragraphs = [l for l in lines[2:] if not l.startswith("●") and not l.startswith("■")]
    
    # 关键要点
    key_points = [l.lstrip("●■").strip() for l in lines if l.startswith("●") or l.startswith("■")]
    
    # 来源
    source_lines = [l for l in reversed(lines[:5]) if any(kw in l for kw in ["来源", "出处", "日期"])]
    
    return {
        "title": title,
        "subtitle": subtitle,
        "paragraphs": paragraphs,
        "key_points": key_points,
        "source": " ".join(source_lines),
        "full_text": full_text,
    }
