"""
文件校验模块 - M01
支持 PDF 和 DOCX 格式校验，提供友好的错误提示。
"""
import os
import uuid
from pathlib import Path
from typing import Tuple

import config


class ValidationError(Exception):
    """校验异常，包含用户友好的错误消息"""
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.message = message
        self.code = code


def validate_file_size(size: int) -> None:
    """校验文件大小"""
    if size > config.MAX_FILE_SIZE:
        max_mb = config.MAX_FILE_SIZE // (1024 * 1024)
        raise ValidationError(
            f"文件大小不能超过 {max_mb}MB",
            code="FILE_TOO_LARGE"
        )


def validate_file_extension(filename: str) -> None:
    """校验文件扩展名"""
    ext = Path(filename).suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        allowed = ", ".join(config.ALLOWED_EXTENSIONS)
        raise ValidationError(
            f"仅支持 {allowed} 格式，当前格式：{ext}",
            code="UNSUPPORTED_FORMAT"
        )


def validate_mime_type(mimetype: str) -> None:
    """校验 MIME 类型"""
    if mimetype not in config.ALLOWED_MIMETYPES:
        raise ValidationError(
            "文件类型不正确，仅支持 PDF、DOCX 格式",
            code="INVALID_MIMETYPE"
        )


def validate_file(filename: str, size: int, mimetype: str) -> Tuple[str, str]:
    """
    综合校验文件。
    返回 (saved_path, original_filename)
    校验失败抛出 ValidationError
    """
    validate_file_size(size)
    validate_file_extension(filename)
    validate_mime_type(mimetype)
    
    # 生成安全文件名
    ext = Path(filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(config.UPLOAD_DIR, safe_name)
    return saved_path, filename
