"""
Tests for app/render.py - M03 长图渲染模块
"""
import pytest
from app.render import render_long_image, _load_font, _wrap_text, CANVAS_WIDTH


class TestRenderLongImage:
    def test_render_returns_valid_png_bytes(self):
        data = {
            "title": "测试标题",
            "subtitle": "测试副标题",
            "source": "测试来源",
            "date": "2025年9月1日",
            "paragraphs": ["这是第一段正文内容。"],
            "key_points": ["要点一：测试内容"],
            "footer": "测试作者",
        }
        png_bytes = render_long_image(data)
        assert isinstance(png_bytes, bytes)
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n', "Not a valid PNG"

    def test_render_with_empty_optional_fields(self):
        data = {
            "title": "仅标题",
            "subtitle": "",
            "source": "",
            "date": "",
            "paragraphs": [],
            "key_points": [],
            "footer": "",
        }
        png_bytes = render_long_image(data)
        assert isinstance(png_bytes, bytes)
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_render_with_missing_title(self):
        data = {
            "paragraphs": ["正文"],
            "key_points": ["要点"],
        }
        png_bytes = render_long_image(data)
        assert isinstance(png_bytes, bytes)
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_render_paragraph_truncation(self):
        long_paragraphs = ["A" * 300] * 10
        data = {
            "title": "长文本测试",
            "paragraphs": long_paragraphs,
            "key_points": ["要点"],
        }
        png_bytes = render_long_image(data)
        assert isinstance(png_bytes, bytes)

    def test_render_key_points_truncation(self):
        many_points = [f"要点{i}: 内容" for i in range(15)]
        data = {
            "title": "多点测试",
            "paragraphs": ["正文"],
            "key_points": many_points,
        }
        png_bytes = render_long_image(data)
        assert isinstance(png_bytes, bytes)


class TestLoadFont:
    def test_load_font_returns_imagem_font(self):
        font = _load_font(36)
        assert font is not None

    def test_load_font_multiple_sizes(self):
        for size in [20, 28, 36, 52]:
            font = _load_font(size)
            assert font is not None


class TestWrapText:
    def test_wrap_text_basic(self):
        from PIL import Image, ImageDraw, ImageFont
        font = _load_font(36)
        draw = ImageDraw.Draw(Image.new("RGB", (100, 100)))
        lines = _wrap_text("hello world", width=20, font=font, draw=draw)
        assert isinstance(lines, list)

    def test_wrap_text_empty(self):
        from PIL import Image, ImageDraw, ImageFont
        font = _load_font(36)
        draw = ImageDraw.Draw(Image.new("RGB", (100, 100)))
        lines = _wrap_text("", width=20, font=font, draw=draw)
        # Empty string results in one empty string from split("\n")
        assert lines == ['']

    def test_wrap_text_newline_preserved(self):
        from PIL import Image, ImageDraw, ImageFont
        font = _load_font(36)
        draw = ImageDraw.Draw(Image.new("RGB", (100, 100)))
        lines = _wrap_text("line1\nline2", width=20, font=font, draw=draw)
        assert len(lines) >= 2