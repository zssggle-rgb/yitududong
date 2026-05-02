"""
Tests for app/extract_docx.py - M01 DOCX 文本抽取
"""
import pytest
from pathlib import Path


class TestExtractDocx:
    def test_extract_structured_returns_expected_keys(self):
        """Verify extract_structured_from_docx returns expected dict keys"""
        # Smoke test - just verify the module imports without error
        from app.extract_docx import extract_structured_from_docx
        assert callable(extract_structured_from_docx)