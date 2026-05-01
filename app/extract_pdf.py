"""
PDF 文本抽取模块 - M01
针对新闻报纸排版 PDF，提取标题、来源、关键章节、三条实践路径等结构化内容。
"""
import re
import fitz  # PyMuPDF
import config


def extract_raw_text(filepath: str) -> str:
    """提取 PDF 文本，每个 block 为一个单元（保留块内换行），按阅读顺序排列"""
    doc = fitz.open(filepath)
    page = doc[0]
    blocks = page.get_text("blocks")
    blocks.sort(key=lambda b: (round(b[1] / 30) * 30, b[0]))
    lines = []
    for b in blocks:
        text = b[4].strip()
        if text:
            lines.append(text)
    doc.close()
    return "\n".join(lines)


def extract_text_from_pdf(filepath: str) -> str:
    """提取 PDF 文本（别名，兼容 main.py 导入）"""
    return extract_raw_text(filepath)


def _merge_adjacent_blocks(blocks: list, max_gap: int = 2) -> list:
    """
    合并相邻的短块（处理报纸排版换行截断）。
    如果当前块不以完整句子结尾，合并下一个块。
    """
    merged = []
    i = 0
    while i < len(blocks):
        current = blocks[i].strip()
        if not current:
            i += 1
            continue
        j = i + 1
        while j < min(i + max_gap + 1, len(blocks)):
            nxt = blocks[j].strip()
            if not nxt:
                break
            # 章节标题模式（如"新技术："、"新药品："）：继续合并
            title_enders = (":", "：")
            if current and current[-1] in title_enders:
                current = current + nxt
                j += 1
                continue
            # 如果当前块不以句号结尾，则合并（空格避免词语粘连）
            elif current and len(current) > 3 and current[-1] not in '。！？；…）)、》」':
                # 但如果下一块是短标题（如栏目名），不合并
                if len(nxt) < 15 and not any(k in nxt for k in ["这", "在", "是", "的"]):
                    break
                current = current + " " + nxt
                j += 1
            else:
                break
        merged.append(current)
        i = j
    return merged


def _truncate_at_title_end(text: str) -> str:
    """
    截取文本直到标题结束（句号、问号、或出现正文标记词为止）。
    用于从混合内容块中提取干净的标题。
    """
    end_markers = "。！？、，：'\"）、》、」"
    # 找标题结束位置
    for i, ch in enumerate(text):
        if ch in end_markers and i > 5:
            return text[:i+1]
    # 如果找到"协同"这样的明确标题词，截取到那里
    for marker in ["协同推动", "编者按", "□", "●", "■"]:
        idx = text.find(marker)
        if idx > 3:
            return text[:idx].strip()
    # 没找到句号，取前60个字符
    return text[:60]


def extract_structured_from_pdf(filepath: str) -> dict:
    """
    从 PDF（新闻报纸排版）中提取结构化内容。
    """
    raw = extract_raw_text(filepath)
    raw_blocks = raw.split("\n")

    if not raw_blocks:
        return {
            "title": "", "subtitle": "", "source": "", "date": "",
            "paragraphs": [], "key_sections": [], "key_points": [],
            "footer": "", "full_text": "", "line_count": 0,
        }

    # 合并相邻块
    merged = _merge_adjacent_blocks(raw_blocks)

    # ── 主标题 ─────────────────────────────────────────────
    # 找"协同推动三新走进商保"作为主标题（y≈283, x=138 位置）
    title = ""
    sidebar_keywords = ["丁云生", "最近几年", "好保险", "笔者的观点", "笔者判断", "2025年9月", "2026年"]
    for line in merged[:40]:
        # 排除侧边栏内容、元信息、不以完整句子结尾的块
        if len(line) < 10:
            continue
        if any(k in line for k in sidebar_keywords):
            continue
        # 直接匹配主标题
        if "协同推动" in line and "三新" in line and "走进商保" in line:
            title = _truncate_at_title_end(line.strip())
            break
        # 备选：含"三新"但不以句号结尾的短行（标题特征）
        if "三新" in line and len(line) < 80 and not any(line.endswith(c) for c in "。！？"):
            if not any(k in line for k in ["2025年", "2026年", "编者按", "丁云生"]):
                title = _truncate_at_title_end(line.strip())
                break

    # ── 副标题 ─────────────────────────────────────────────
    subtitle = ""
    for line in merged[:30]:
        if "推动健康险高质量发展系列专题" in line:
            subtitle = line.strip()
            break
        if "深读" in line and len(line) < 80 and not subtitle:
            subtitle = line.strip()

    # ── 来源和日期 ─────────────────────────────────────────
    date = ""
    source = "中国银行保险报"
    for line in merged:
        m = re.search(r"(\d{4}年\d+月\d+日[星期\w]*)", line)
        if m:
            date = m.group(1)

    # ── 关键章节（新技术/新药品/新器械 完整标题）───────────
    # 取关键词后最多120个字符（完整章节标题长度）
    key_sections = []
    seen = set()
    for line in merged:
        clean = re.sub(r"\s+", "", line)
        for kw in ["新技术：", "新药品：", "新器械："]:
            idx = clean.find(kw)
            if idx >= 0:
                segment = clean[idx:idx + 120]
                if segment not in seen:
                    key_sections.append(segment)
                    seen.add(segment)

    # ── 正文段落 ─────────────────────────────────────────
    skip_prefixes = ("□", "■", "●", "来源", "出处", "编辑", "制作",
                      "责校", "邮箱", "电话", "CHINA BANKING", "深读",
                      "In Depth", "业内声音")
    meta_phrase = "推动健康险高质量发展系列专题之二"
    paragraphs = []
    for line in merged:
        if len(line) < 15:
            continue
        if any(line.startswith(p) for p in skip_prefixes):
            continue
        if meta_phrase in line:
            continue
        if any(x in line for x in ["邮箱：", "电话：", "责校：", "编辑：", "制作："]):
            continue
        if re.match(r"^\d{4}年\d+月\d+日", line):
            continue
        paragraphs.append(line)

    # ── 三条实践路径要点 ─────────────────────────────────
    key_points = []
    for line in merged:
        stripped = line.strip()
        if len(stripped) < 5:
            continue
        if any(stripped.startswith(p) for p in skip_prefixes):
            continue
        m = re.match(r"^第[一二三四五][、，](.+)", stripped)
        if m:
            point_text = m.group(1).strip()
            if len(point_text) > 5:
                key_points.append(stripped)
    # 扩展合并：将连续短块合并为完整要点
    expanded_points = []
    for pt in key_points:
        # 如果要点以句号结尾或较长，说明已经是完整段落
        if pt[-1] in '。！？' and len(pt) > 40:
            expanded_points.append(pt)
        else:
            # 尝试扩展：找当前要点在 merged 中的位置，合并后续块
            idx = -1
            for i, line in enumerate(merged):
                if line.strip() == pt.strip():
                    idx = i
                    break
            if idx >= 0:
                # 继续向前合并最多5个相邻块
                extended = pt
                for k in range(idx + 1, min(idx + 6, len(merged))):
                    nxt = merged[k].strip()
                    if not nxt:
                        break
                    if nxt.startswith('第') or nxt.startswith('HPV') or nxt.startswith('该研') or nxt.startswith('一位') or nxt.startswith('这种') or nxt.startswith('鉴于'):
                        break
                    extended = extended + nxt
                expanded_points.append(extended)
            else:
                expanded_points.append(pt)

    # ── 底部作者信息 ─────────────────────────────────────
    footer = ""
    for line in reversed(merged):
        stripped = line.strip()
        if any(k in stripped for k in ["作者系", "重疾不重", "丁云生"]):
            footer = stripped
            break

    return {
        "title": title,
        "subtitle": subtitle,
        "source": source,
        "date": date,
        "paragraphs": paragraphs[:20],
        "key_sections": key_sections[:5],
        "key_points": expanded_points[:6],
        "footer": footer,
        "full_text": raw,
        "line_count": len(raw_blocks),
    }


def extract_reference_pdf() -> dict:
    """读取参考 PDF 并返回抽取结果（M01 演示用）"""
    return extract_structured_from_pdf(config.REFERENCE_PDF)


if __name__ == "__main__":
    result = extract_reference_pdf()
    print("=== 参考 PDF 抽取结果（M01）===")
    print(f"标题: {result['title']}")
    print(f"副标题: {result['subtitle']}")
    print(f"来源: {result['source']} | {result['date']}")
    print(f"关键章节({len(result['key_sections'])}):")
    for s in result['key_sections']:
        print(f"  • {s}")
    print(f"段落数: {len(result['paragraphs'])}")
    print(f"三条路径要点({len(result['key_points'])}):")
    for pt in result["key_points"]:
        print(f"  • {pt[:100]}")
    print(f"底部说明: {result['footer']}")
    print()
    print("前5段正文:")
    for p in result["paragraphs"][:5]:
        print(f"  {p[:90]}")
