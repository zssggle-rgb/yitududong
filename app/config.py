import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "yitududong-dev-secret-2026")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", "output_imgs")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
    PLAYWRIGHT_TIMEOUT = int(os.environ.get("PLAYWRIGHT_TIMEOUT", "60000"))
    SCREENSHOT_WIDTH = int(os.environ.get("SCREENSHOT_WIDTH", "1080"))

    # 模板配置
    TEMPLATE_COLOR_PRIMARY = "#1a73e8"   # 蓝色主色
    TEMPLATE_COLOR_SECONDARY = "#e8f0fe"  # 浅蓝背景
    TEMPLATE_COLOR_TEXT = "#202124"      # 深灰文字
    TEMPLATE_COLOR_ACCENT = "#1967d2"    # 深蓝强调
    TEMPLATE_WIDTH = 1080               # 图片宽度 px
