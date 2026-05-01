"""DOCX 解析器单元测试"""
import pytest
from app.parsers.docx_parser import parse_docx

def test_parse_empty_docx():
    """测试空文档"""
    result = parse_docx("nonexistent.docx")
    assert "title" in result
    assert "summary" in result
    assert "points" in result
    assert "footer" in result

def test_result_structure():
    result = parse_docx("nonexistent.docx")
    assert isinstance(result["title"], str)
    assert isinstance(result["summary"], str)
    assert isinstance(result["points"], list)
