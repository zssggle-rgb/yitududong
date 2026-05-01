import os
import pytest
from app.extract_pdf import extract_raw_text, extract_structured_from_pdf

REF_PDF = "/Users/sjs/Downloads/05B20260430C_l.pdf"
has_ref_pdf = os.path.exists(REF_PDF)


class TestExtractRawText:
    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_reference_pdf_returns_string(self):
        """Reference PDF should return non-empty text"""
        text = extract_raw_text(REF_PDF)
        assert isinstance(text, str)
        assert len(text) > 100

    def test_nonexistent_file_raises(self):
        with pytest.raises(Exception):  # PyMuPDF raises fitz.FitzError or similar
            extract_raw_text("/nonexistent/file.pdf")


class TestExtractStructuredFromPdf:
    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_reference_pdf_has_title(self):
        """Reference PDF should extract a title"""
        result = extract_structured_from_pdf(REF_PDF)
        assert result["title"] != ""
        assert len(result["title"]) >= 5

    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_reference_pdf_has_source(self):
        result = extract_structured_from_pdf(REF_PDF)
        assert result["source"] != ""

    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_reference_pdf_has_key_sections(self):
        result = extract_structured_from_pdf(REF_PDF)
        assert len(result["key_sections"]) >= 1

    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_reference_pdf_has_key_points(self):
        result = extract_structured_from_pdf(REF_PDF)
        assert len(result["key_points"]) >= 1

    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_result_has_required_keys(self):
        result = extract_structured_from_pdf(REF_PDF)
        required_keys = ["title", "subtitle", "source", "date", "paragraphs",
                         "key_sections", "key_points", "footer", "full_text", "line_count"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    @pytest.mark.skipif(not has_ref_pdf, reason="Reference PDF not available in CI environment")
    def test_full_text_is_nonempty(self):
        result = extract_structured_from_pdf(REF_PDF)
        assert len(result["full_text"]) > 500