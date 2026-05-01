"""
DOCX 解析器：提取文档结构化信息
使用 python-docx 提取段落和样式
"""
import re
from docx import Document


def parse_docx(file_path):
    """
    解析 DOCX 文件，提取结构化信息。
    返回字典包含：title, summary, points, footer
    """
    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        return {
            "title": "文档标题",
            "summary": "文档内容为空",
            "points": [],
            "footer": "来源：Word 文档"
        }

    # 提取标题
    title = ""
    for para in paragraphs[:5]:
        if len(para) >= 5:
            # 优先找标题样式的段落
            title = para
            break
    if not title:
        title = paragraphs[0]

    # 提取摘要
    summary_lines = []
    in_body = False
    body_count = 0
    for para in paragraphs:
        if para == title:
            in_body = True
            continue
        if in_body:
            if len(para) > 20:
                summary_lines.append(para)
                body_count += 1
                if body_count >= 3:
                    break

    summary = " ".join(summary_lines) if summary_lines else ""

    # 提取分条要点
    points = []
    for para in paragraphs:
        if re.match(r"^\d+[.、]\s", para) or re.match(r"^[一二三四五六七八九十]+[、.]\s", para):
            points.append(para)
        elif re.match(r"^[•\-\*]\s", para):
            points.append(para)
        elif para.startswith("●"):
            points.append(para)

    if not points:
        for para in paragraphs[3:]:
            if 15 < len(para) < 200:
                points.append(para)
                if len(points) >= 5:
                    break

    # 提取底部信息
    footer = ""
    for para in paragraphs[-5:]:
        if any(k in para for k in ["来源", "发布", "日期", "时间", "年", "月", "日"]):
            footer = para
            break
    if not footer:
        footer = paragraphs[-1] if paragraphs else ""

    return {
        "title": title,
        "summary": summary,
        "points": points[:10],
        "footer": footer,
        "raw_text": "\n".join(paragraphs[:50])
    }
