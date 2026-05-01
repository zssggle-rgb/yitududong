"""
Tests for app/validate.py - M01 文件校验
"""
import pytest
from pathlib import Path
from app.validate import (
    validate_file_size,
    validate_file_extension,
    validate_mime_type,
    validate_file,
    ValidationError,
)


class TestValidateFileSize:
    def test_valid_size(self):
        validate_file_size(1024 * 1024)  # 1MB - ok

    def test_at_limit(self):
        validate_file_size(20 * 1024 * 1024)  # exactly 20MB - ok

    def test_oversize_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(21 * 1024 * 1024)
        assert exc_info.value.code == "FILE_TOO_LARGE"


class TestValidateFileExtension:
    def test_pdf_ok(self):
        validate_file_extension("report.pdf")

    def test_docx_ok(self):
        validate_file_extension("report.docx")

    def test_uppercase_ext_ok(self):
        validate_file_extension("report.PDF")

    def test_unsupported_ext_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_file_extension("report.txt")
        assert exc_info.value.code == "UNSUPPORTED_FORMAT"


class TestValidateMimeType:
    def test_pdf_mimetype_ok(self):
        validate_mime_type("application/pdf")

    def test_docx_mimetype_ok(self):
        validate_mime_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    def test_wrong_mimetype_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_mime_type("text/plain")
        assert exc_info.value.code == "INVALID_MIMETYPE"


class TestValidateFile:
    def test_valid_pdf(self, tmp_path):
        path, name = validate_file("test.pdf", 1024, "application/pdf")
        assert Path(path).name.endswith(".pdf")
        assert name == "test.pdf"
        # File path should be in uploads dir
        assert "uploads" in path

    def test_valid_docx(self, tmp_path):
        path, name = validate_file("test.docx", 1024,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert name == "test.docx"

    def test_oversize_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_file("big.pdf", 30 * 1024 * 1024, "application/pdf")
        assert exc_info.value.code == "FILE_TOO_LARGE"

    def test_bad_ext_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_file("bad.txt", 1024, "text/plain")
        assert exc_info.value.code == "UNSUPPORTED_FORMAT"