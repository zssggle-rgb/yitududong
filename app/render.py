"""
长图渲染模块 - M03/M04
使用 Pillow 将结构化内容渲染为蓝色政务风中文长图 PNG。
"""
import io
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 蓝色政务风配色
PRIMARY_COLOR = (26, 95, 180)       # #1a5fb4
PRIMARY_LIGHT = (53, 132, 228)     # #3584e4
BG_WHITE = (255, 255, 255)
BG_LIGHT = (232, 240, 254)          # #e8f0fe
TEXT_DARK = (36, 41, 47)            # #24292f
TEXT_MUTED = (87, 96, 106)          # #57606a
ACCENT_GOLD = (253, 184, 19)       # #fdb813

# 画布参数
CANVAS_WIDTH = 1080
MARGIN_H = 48
SECTION_GAP = 36


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load system font with cross-platform fallback chain.

    Priority:
    1. macOS: PingFang (苹方), STHeiti (黑体)
    2. Windows: msyh (微软雅黑)
    3. Linux: DejaVuSans, LiberationSans, FreeSans, NotoSansCJK, wqy-microhei
    4. Final fallback: ImageFont.load_default()

    Args:
        size: font size in points
        bold: currently unused, reserved for future bold-variant loading
    Returns:
        PIL FreeTypeFont instance
    """
    # macOS fonts
    mac_fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    # Windows font
    windows_fonts = [
        "C:/Windows/Fonts/msyh.ttc",
    ]
    # Linux fonts
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]

    # Arial as last resort before Linux fallbacks
    arial_font = "/Library/Fonts/Arial.ttf"

    for path in mac_fonts + windows_fonts + [arial_font] + linux_fonts:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass

    # Final fallback: minimal bitmap font (always available)
    return ImageFont.load_default()


def _wrap_text(text: str, width: int, font: ImageFont.FreeTypeFont, draw: ImageDraw.Draw) -> list:
    """智能换行，返回行列表"""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        wrapped = textwrap.wrap(paragraph, width=width)
        lines.extend(wrapped if wrapped else [""])
    return lines


def render_long_image(data: dict) -> bytes:
    """
    将结构化内容渲染为长图 PNG。
    data: {
        "title": str,
        "subtitle": str,
        "source": str,
        "date": str,
        "paragraphs": list[str],
        "key_points": list[str],
        "footer": str,
    }
    Returns PNG bytes.
    """
    # 字体
    font_title = _load_font(52, bold=True)
    font_subtitle = _load_font(36)
    font_body = _load_font(38)
    font_point = _load_font(36)
    font_label = _load_font(28)
    font_footer = _load_font(26)

    # 顶部装饰条高度
    top_bar_h = 120
    # 标题区高度
    title_area_h = 160
    # 摘要区高度
    summary_h = 200
    # 每个要点卡片高度
    point_card_h = 120
    # 底部说明区高度
    footer_h = 100
    # 底部装饰条高度
    bottom_bar_h = 80

    # 预计算段落文本总高度
    paragraph_lines = []
    for para in (data.get("paragraphs", []) or [])[:15]:
        wrapped = _wrap_text(para, width=44, font=font_body, draw=None)
        paragraph_lines.extend(wrapped)

    paragraph_area_h = len(paragraph_lines) * 56 + 60

    # 预计算要点卡片总高度
    points = data.get("key_points", []) or []
    point_area_h = len(points) * point_card_h + 40

    # 计算总高度
    content_top = top_bar_h + title_area_h + summary_h + paragraph_area_h + point_area_h + footer_h + bottom_bar_h + SECTION_GAP * 6
    canvas_height = content_top

    # 创建画布
    img = Image.new("RGB", (CANVAS_WIDTH, canvas_height), BG_WHITE)
    draw = ImageDraw.Draw(img)

    y = 0

    # ── 顶部装饰条 ──────────────────────────────────────────
    for x in range(CANVAS_WIDTH):
        ratio = x / CANVAS_WIDTH
        r = int(PRIMARY_COLOR[0] + (PRIMARY_LIGHT[0] - PRIMARY_COLOR[0]) * ratio)
        g = int(PRIMARY_COLOR[1] + (PRIMARY_LIGHT[1] - PRIMARY_COLOR[1]) * ratio)
        b = int(PRIMARY_COLOR[2] + (PRIMARY_LIGHT[2] - PRIMARY_COLOR[2]) * ratio)
        draw.line([(x, 0), (x, top_bar_h)], fill=(r, g, b))
    y += top_bar_h + SECTION_GAP

    # ── 标题区 ─────────────────────────────────────────────
    title = data.get("title", "") or "一图读懂政策"
    wrapped_title = _wrap_text(title, width=36, font=font_title, draw=None)
    for line in wrapped_title:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        text_w = bbox[2] - bbox[0]
        x = (CANVAS_WIDTH - text_w) // 2
        draw.text((x, y), line, fill=TEXT_DARK, font=font_title)
        y += 64
    y += 20
    # 副标题
    subtitle = data.get("subtitle", "") or ""
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        text_w = bbox[2] - bbox[0]
        x = (CANVAS_WIDTH - text_w) // 2
        draw.text((x, y), subtitle, fill=TEXT_MUTED, font=font_subtitle)
        y += 52
    y += SECTION_GAP

    # ── 正文摘要区 ─────────────────────────────────────────
    draw.rectangle([(MARGIN_H, y), (CANVAS_WIDTH - MARGIN_H, y + 6)], fill=PRIMARY_COLOR)
    y += 24

    if paragraph_lines:
        for line in paragraph_lines:
            if line:
                draw.text((MARGIN_H, y), line, fill=TEXT_DARK, font=font_body)
                y += 56
    y += SECTION_GAP

    # ── 分条政策卡片 ────────────────────────────────────────
    draw.rectangle([(MARGIN_H, y), (CANVAS_WIDTH - MARGIN_H, y + 6)], fill=PRIMARY_COLOR)
    y += 24

    if points:
        for pt in points:
            # 卡片背景
            card_rect = [(MARGIN_H, y), (CANVAS_WIDTH - MARGIN_H, y + point_card_h - 12)]
            draw.rectangle(card_rect, fill=BG_LIGHT, outline=PRIMARY_COLOR, width=2)
            # 左侧装饰条
            draw.rectangle([(MARGIN_H, y), (MARGIN_H + 8, y + point_card_h - 12)], fill=PRIMARY_COLOR)
            # 文字
            pt_text = pt if len(pt) <= 60 else pt[:57] + "..."
            draw.text((MARGIN_H + 28, y + 20), pt_text, fill=TEXT_DARK, font=font_point)
            y += point_card_h
    y += SECTION_GAP

    # ── 底部说明 ────────────────────────────────────────────
    draw.rectangle([(MARGIN_H, y), (CANVAS_WIDTH - MARGIN_H, y + 4)], fill=PRIMARY_COLOR)
    y += 16

    source = data.get("source", "") or ""
    date = data.get("date", "") or ""
    footer_parts = [p for p in [source, date] if p]
    if footer_parts:
        footer_text = " | ".join(footer_parts)
        bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
        text_w = bbox[2] - bbox[0]
        x = (CANVAS_WIDTH - text_w) // 2
        draw.text((x, y), footer_text, fill=TEXT_MUTED, font=font_footer)
        y += 40

    author = data.get("footer", "") or ""
    if author:
        bbox = draw.textbbox((0, 0), author, font=font_footer)
        text_w = bbox[2] - bbox[0]
        x = (CANVAS_WIDTH - text_w) // 2
        draw.text((x, y), author, fill=TEXT_MUTED, font=font_footer)
        y += 36
    y += SECTION_GAP

    # ── 底部装饰条 ──────────────────────────────────────────
    for x in range(CANVAS_WIDTH):
        ratio = x / CANVAS_WIDTH
        r = int(PRIMARY_COLOR[0] + (PRIMARY_LIGHT[0] - PRIMARY_COLOR[0]) * ratio)
        g = int(PRIMARY_COLOR[1] + (PRIMARY_LIGHT[1] - PRIMARY_COLOR[1]) * ratio)
        b = int(PRIMARY_COLOR[2] + (PRIMARY_LIGHT[2] - PRIMARY_COLOR[2]) * ratio)
        draw.line([(x, canvas_height - bottom_bar_h), (x, canvas_height)], fill=(r, g, b))

    # 保存到bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()