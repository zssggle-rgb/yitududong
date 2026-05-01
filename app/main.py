"""
yitududong - M01 文档接入与上传
FastAPI 主应用：提供文件上传入口、格式校验、参考 PDF 文本抽取接口。
"""
import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

import config
from app.validate import validate_file, ValidationError
from app.extract_pdf import extract_structured_from_pdf, extract_text_from_pdf
from app.extract_docx import extract_structured_from_docx

app = FastAPI(
    title="一图读懂 - 文档转长图",
    version="1.0.0",
    description="M01 模块：PDF/DOCX 上传入口与文本抽取",
)

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "module": "M01", "service": "yitududong"}


@app.get("/", response_class=HTMLResponse)
async def index_page():
    """主页 - 文件上传页面"""
    html_path = static_dir / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    文件上传接口。
    - 支持 PDF 和 DOCX 格式
    - 文件大小限制 20MB
    - 校验失败返回友好错误提示
    成功时返回提取的文本结构（后续 M02 模块继续处理）
    """
    try:
        # 读取文件大小
        content = await file.read()
        file_size = len(content)
        
        # 写入临时文件
        saved_path, original_name = validate_file(
            filename=file.filename or "unknown",
            size=file_size,
            mimetype=file.content_type or "",
        )
        
        with open(saved_path, "wb") as f:
            f.write(content)
        
        # 根据扩展名选择提取器
        ext = Path(saved_path).suffix.lower()
        
        if ext == ".pdf":
            structured = extract_structured_from_pdf(saved_path)
        elif ext == ".docx":
            structured = extract_structured_from_docx(saved_path)
        else:
            raise ValidationError("不支持的文件格式", code="UNSUPPORTED_FORMAT")
        
        # 清理临时文件
        try:
            os.remove(saved_path)
        except Exception:
            pass
        
        if not structured.get("full_text"):
            raise ValidationError(
                "未检测到有效内容，请检查文件是否包含文字",
                code="EMPTY_CONTENT"
            )
        
        return JSONResponse({
            "success": True,
            "filename": original_name,
            "size": file_size,
            "ext": ext,
            "module": "M01",
            "stage": "upload_ok",
            "data": {
                "title": structured["title"],
                "subtitle": structured.get("subtitle", ""),
                "paragraphs": structured["paragraphs"][:10],
                "key_points": structured["key_points"],
                "source": structured.get("source", ""),
                "line_count": structured.get("line_count", 0),
            }
        })
        
    except ValidationError as ve:
        return JSONResponse({
            "success": False,
            "error": ve.message,
            "code": ve.code,
        }, status_code=400)


@app.get("/reference-extract")
async def reference_extract():
    """
    参考 PDF 文本抽取演示接口（M01 内部验证用）。
    读取 /Users/sjs/Downloads/05B20260430C_l.pdf 并返回抽取结果。
    """
    import os
    ref_pdf = config.REFERENCE_PDF
    if not os.path.exists(ref_pdf):
        raise HTTPException(
            status_code=404,
            detail=f"参考 PDF 不存在: {ref_pdf}"
        )
    
    result = extract_structured_from_pdf(ref_pdf)
    return JSONResponse({
        "success": True,
        "source": ref_pdf,
        "module": "M01",
        "stage": "reference_extraction",
        "data": result,
    })


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
