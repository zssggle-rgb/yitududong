"""
PDF 解析器：提取文档结构化信息
使用 pypdf 提取文本和层级
"""
import re
from pypdf import PdfReader


def parse_pdf(file_path):
    """
    解析 PDF 文件，提取结构化信息。
    返回字典包含：title, summary, points, footer
    """
    try:
        reader = PdfReader(file_path)
    except Exception:
        return {
            "title": "文档标题",
            "summary": "PDF 读取失败",
            "points": [],
            "footer": "来源：PDF 文档"
        }

    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    if not full_text.strip():
        return {
            "title": "未提取到文本（可能是扫描件）",
            "summary": "PDF 中未检测到可编辑文本，请使用文字型 PDF。",
            "points": [],
            "footer": "来源：PDF 文档"
        }

    lines = [l.strip() for l in full_text.split("\n") if l.strip()]

    # 提取标题：取前几行中非短句、较长的行
    title = ""
    for line in lines[:10]:
        if len(line) >= 8:
            title = line
            break
    if not title:
        title = lines[0] if lines else "文档标题"

    # 提取正文摘要：从标题后取 1-3 行
    summary_lines = []
    in_body = False
    body_count = 0
    for line in lines:
        if line == title:
            in_body = True
            continue
        if in_body:
            if len(line) > 20:
                summary_lines.append(line)
                body_count += 1
                if body_count >= 3:
                    break

    summary = " ".join(summary_lines) if summary_lines else ""

    # 提取分条要点（数字编号、•、- 等）
    points = []
    for line in lines:
        if re.match(r"^\d+[.、]\s", line) or re.match(r"^[一二三四五六七八九十]+[、.]\s", line):
            points.append(line)
        elif re.match(r"^[•\-\*]\s", line):
            points.append(line)

    # 如果没找到明确编号点，尝试取较长的行作为要点
    if not points:
        for line in lines[3:]:
            if len(line) > 15 and len(line) < 200:
                points.append(line)
                if len(points) >= 5:
                    break

    # 提取底部信息（来源、日期等）
    footer = ""
    for line in lines[-5:]:
        if any(k in line for k in ["来源", "发布", "日期", "时间", "年", "月", "日"]):
            footer = line
            break
    if not footer:
        footer = lines[-1] if lines else ""

    return {
        "title": title,
        "summary": summary,
        "points": points[:10],
        "footer": footer,
        "raw_text": full_text[:5000]
    }
