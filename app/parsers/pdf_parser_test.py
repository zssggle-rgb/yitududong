"""PDF 解析器单元测试"""
import pytest
import tempfile
from pathlib import Path
from app.parsers.pdf_parser import parse_pdf

def test_parse_empty_text():
    """测试空文本 PDF"""
    result = parse_pdf("nonexistent.pdf")
    assert "title" in result
    assert "summary" in result
    assert "points" in result
    assert "footer" in result

def test_parse_result_structure():
    """测试返回结构"""
    result = parse_pdf("nonexistent.pdf")
    assert isinstance(result["title"], str)
    assert isinstance(result["summary"], str)
    assert isinstance(result["points"], list)
    assert isinstance(result["footer"], str)
