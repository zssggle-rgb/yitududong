"""
yitududong - M04 预览下载与前端体验
FastAPI 主应用：提供文件上传、文本抽取、长图预览和 PNG 下载。
"""
import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

import config
from app.validate import validate_file, ValidationError
from app.extract_pdf import extract_structured_from_pdf, extract_text_from_pdf
from app.extract_docx import extract_structured_from_docx
from app.render import render_long_image


class GenerateData(BaseModel):
    """输入数据 schema，防止 OOM"""
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: str = Field(default="", max_length=200)
    source: str = Field(default="", max_length=100)
    date: str = Field(default="", max_length=50)
    paragraphs: list[str] = Field(default_factory=list, max_length=20)
    key_points: list[str] = Field(default_factory=list, max_length=20)
    footer: str = Field(default="", max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "协同推动三新走进商保",
                "subtitle": "推动健康险高质量发展系列专题",
                "source": "中国银行保险报",
                "date": "2025年9月1日",
                "paragraphs": ["正文..."],
                "key_points": ["第一条、..."],
                "footer": "作者系..."
            }
        }
    }


MAX_PARAGRAPHS_LIMIT = 20
MAX_KEY_POINTS_LIMIT = 20
MAX_PARAGRAPH_CHARS = 2000  # per paragraph


app = FastAPI(
    title="一图读懂 - 文档转长图",
    version="1.0.0",
    description="M04 模块：预览下载与前端体验",
)

# CORS middleware - allow all origins for development/QA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "module": "M04", "service": "yitududong"}


@app.get("/", response_class=HTMLResponse)
async def index_page():
    """主页 - 文件上传与预览下载页面"""
    html_path = static_dir / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)


def _cleanup_temp_file(path: str) -> None:
    """安全清理临时文件，忽略所有异常"""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    文件上传接口。
    - 支持 PDF 和 DOCX 格式
    - 文件大小限制 20MB
    - 校验失败返回友好错误提示
    成功时返回提取的文本结构（后续 M02/M03/M04 模块继续处理）
    """
    saved_path = None
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
            "module": "M04",
            "stage": "upload_ok",
            "data": {
                "title": structured.get("title", ""),
                "subtitle": structured.get("subtitle", ""),
                "paragraphs": structured.get("paragraphs", [])[:10],
                "key_points": structured.get("key_points", []),
                "source": structured.get("source", ""),
                "date": structured.get("date", ""),
                "footer": structured.get("footer", ""),
                "line_count": structured.get("line_count", 0),
                "full_text": structured.get("full_text", ""),
            }
        })

    except ValidationError as ve:
        return JSONResponse({
            "success": False,
            "error": ve.message,
            "code": ve.code,
        }, status_code=400)
    finally:
        # 无论成功还是异常，都要清理临时文件
        if saved_path:
            _cleanup_temp_file(saved_path)


@app.post("/generate")
async def generate_long_image(data: GenerateData):
    """
    生成预览长图。
    接收结构化数据，渲染为 PNG。
    输入验证：限制 paragraphs/key_points 数量和每段长度，防止 OOM。
    """
    try:
        # OOM 保护：限制 paragraphs 和 key_points 的总数据量
        paragraphs = data.paragraphs[:MAX_PARAGRAPHS_LIMIT]
        key_points = data.key_points[:MAX_KEY_POINTS_LIMIT]

        # 每段限制字符数
        paragraphs = [p[:MAX_PARAGRAPH_CHARS] for p in paragraphs]

        render_data = {
            "title": data.title,
            "subtitle": data.subtitle,
            "source": data.source,
            "date": data.date,
            "paragraphs": paragraphs,
            "key_points": key_points,
            "footer": data.footer,
        }

        # 渲染 PNG
        png_bytes = render_long_image(render_data)

        return Response(content=png_bytes, media_type="image/png")

    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"生成预览失败：{str(e)}",
            "code": "RENDER_ERROR",
        }, status_code=500)


@app.get("/reference-extract")
async def reference_extract():
    """
    参考 PDF 文本抽取演示接口（M01 内部验证用）。
    读取 config.REFERENCE_PDF 并返回抽取结果。
    不暴露完整本地路径。
    """
    ref_pdf = config.REFERENCE_PDF
    if not os.path.exists(ref_pdf):
        raise HTTPException(
            status_code=404,
            detail="参考 PDF 不存在"
        )

    result = extract_structured_from_pdf(ref_pdf)
    return JSONResponse({
        "success": True,
        "source": "reference_pdf",  # 不暴露完整本地路径
        "module": "M01",
        "stage": "reference_extraction",
        "data": result,
    })


@app.get("/reference-generate")
async def reference_generate():
    """
    参考 PDF 一键生成演示接口（M04 验证用）。
    读取参考 PDF，抽取内容，直接渲染 PNG 并返回。
    """
    ref_pdf = config.REFERENCE_PDF
    if not os.path.exists(ref_pdf):
        raise HTTPException(
            status_code=404,
            detail="参考 PDF 不存在"
        )

    structured = extract_structured_from_pdf(ref_pdf)

    render_data = {
        "title": structured.get("title", "一图读懂"),
        "subtitle": structured.get("subtitle", ""),
        "source": structured.get("source", ""),
        "date": structured.get("date", ""),
        "paragraphs": structured.get("paragraphs", [])[:10],
        "key_points": structured.get("key_points", [])[:8],
        "footer": structured.get("footer", ""),
    }

    png_bytes = render_long_image(render_data)
    return Response(content=png_bytes, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
