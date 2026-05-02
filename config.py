"""
配置文件 - yitududong M01
"""
import os

# 上传配置
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIMETYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# 存储配置
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 服务配置
HOST = "0.0.0.0"
PORT = 18083

# 参考 PDF 路径（用于 M01 文本抽取演示）
REFERENCE_PDF = "/Users/sjs/Downloads/05B20260430C_l.pdf"
