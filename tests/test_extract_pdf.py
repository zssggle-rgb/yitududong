"""
Tests for app/extract_pdf.py - M01 PDF 文本抽取
"""
import pytest
from app.extract_pdf import extract_raw_text, extract_structured_from_pdf


class TestExtractRawText:
    def test_reference_pdf_returns_string(self):
        """Reference PDF should return non-empty text"""
        text = extract_raw_text("/Users/sjs/Downloads/05B20260430C_l.pdf")
        assert isinstance(text, str)
        assert len(text) > 100

    def test_nonexistent_file_raises(self):
        with pytest.raises(Exception):  # PyMuPDF raises fitz.FitzError or similar
            extract_raw_text("/nonexistent/file.pdf")


class TestExtractStructuredFromPdf:
    def test_reference_pdf_has_title(self):
        """Reference PDF should extract a title"""
        result = extract_structured_from_pdf("/Users/sjs/Downloads/05B20260430C_l.pdf")
        assert result["title"] != ""
        assert len(result["title"]) >= 5

    def test_reference_pdf_has_source(self):
        result = extract_structured_from_pdf("/Users/sjs/Downloads/05B20260430C_l.pdf")
        assert result["source"] != ""

    def test_reference_pdf_has_key_sections(self):
        result = extract_structured_from_pdf("/Users/sjs/Downloads/05B20260430C_l.pdf")
        assert len(result["key_sections"]) >= 1

    def test_reference_pdf_has_key_points(self):
        result = extract_structured_from_pdf("/Users/sjs/Downloads/05B20260430C_l.pdf")
        assert len(result["key_points"]) >= 1

    def test_result_has_required_keys(self):
        result = extract_structured_from_pdf("/Users/sjs/Downloads/05B20260430C_l.pdf")
        required_keys = ["title", "subtitle", "source", "date", "paragraphs",
                         "key_sections", "key_points", "footer", "full_text", "line_count"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_full_text_is_nonempty(self):
        result = extract_structured_from_pdf("/Users/sjs/Downloads/05B20260430C_l.pdf")
        assert len(result["full_text"]) > 500