from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx

def parse_document(file_path):
    """统一解析入口，自动识别文件类型"""
    ext = file_path.lower().split('.')[-1]
    if ext == 'pdf':
        return parse_pdf(file_path)
    elif ext in ('docx', 'doc'):
        return parse_docx(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {ext}")
