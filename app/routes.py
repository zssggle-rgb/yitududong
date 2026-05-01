"""
yitududong Flask 路由
实现：上传 → 解析 → 生成 → 预览 → 下载
"""
import os
import uuid
import datetime
from flask import Blueprint, request, jsonify, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from app.parsers import parse_document
from app.screenshot import render_html_to_screenshot, cleanup_old_outputs

bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def index():
    """首页 / 上传页面"""
    return render_template("index.html")


@bp.route("/upload", methods=["POST"])
def upload():
    """
    文件上传接口
    接收 PDF/DOCX，返回预览页面
    """
    if "file" not in request.files:
        return jsonify({"error": "未检测到文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "文件名为空"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件类型，仅支持 PDF/DOCX"}), 400

    # 保存上传文件
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = os.environ.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)
    file.save(file_path)

    try:
        # 解析文档
        parsed = parse_document(file_path)
    except Exception as e:
        return jsonify({"error": f"文档解析失败: {str(e)}"}), 500
    finally:
        # 清理上传文件（异步，忽略异常）
        try:
            os.remove(file_path)
        except Exception:
            pass

    # 渲染 HTML
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    width = int(os.environ.get("SCREENSHOT_WIDTH", "1080"))
    html_content = render_template(
        "card.html",
        title=parsed.get("title", "文档标题"),
        summary=parsed.get("summary", ""),
        points=parsed.get("points", []),
        footer=parsed.get("footer", ""),
        width=width,
        timestamp=timestamp
    )

    # 生成截图
    output_dir = os.environ.get("OUTPUT_FOLDER", "output_imgs")
    try:
        img_path = render_html_to_screenshot(html_content, output_dir, width=width)
    except Exception as e:
        return jsonify({"error": f"截图生成失败: {str(e)}"}), 500

    # 返回预览页面（自动展示生成的图片）
    img_filename = os.path.basename(img_path)
    return render_template(
        "preview.html",
        img_filename=img_filename,
        title=parsed.get("title", ""),
        summary=parsed.get("summary", ""),
        points=parsed.get("points", []),
        footer=parsed.get("footer", "")
    )


@bp.route("/preview/<img_filename>")
def preview(img_filename):
    """预览指定图片"""
    output_dir = os.environ.get("OUTPUT_FOLDER", "output_imgs")
    img_path = os.path.join(output_dir, img_filename)
    if not os.path.exists(img_path):
        return "图片不存在或已过期", 404
    return send_file(img_path, mimetype="image/png")


@bp.route("/download/<img_filename>")
def download(img_filename):
    """下载图片"""
    output_dir = os.environ.get("OUTPUT_FOLDER", "output_imgs")
    img_path = os.path.join(output_dir, img_filename)
    if not os.path.exists(img_path):
        return "图片不存在或已过期", 404
    return send_file(
        img_path,
        as_attachment=True,
        download_name=f"yitududong_{img_filename}",
        mimetype="image/png"
    )


@bp.route("/api/upload", methods=["POST"])
def api_upload():
    """
    API 方式上传
    返回 JSON: {img_url, title, summary}
    """
    if "file" not in request.files:
        return jsonify({"error": "未检测到文件"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "无效文件"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = os.environ.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)
    file.save(file_path)

    try:
        parsed = parse_document(file_path)
    except Exception as e:
        return jsonify({"error": f"解析失败: {str(e)}"}), 500
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    width = int(os.environ.get("SCREENSHOT_WIDTH", "1080"))
    html_content = render_template(
        "card.html",
        title=parsed.get("title", "文档标题"),
        summary=parsed.get("summary", ""),
        points=parsed.get("points", []),
        footer=parsed.get("footer", ""),
        width=width,
        timestamp=timestamp
    )

    output_dir = os.environ.get("OUTPUT_FOLDER", "output_imgs")
    try:
        img_path = render_html_to_screenshot(html_content, output_dir, width=width)
    except Exception as e:
        return jsonify({"error": f"截图生成失败: {str(e)}"}), 500

    img_filename = os.path.basename(img_path)
    img_url = url_for("main.preview", img_filename=img_filename, _external=True)
    download_url = url_for("main.download", img_filename=img_filename, _external=True)

    return jsonify({
        "success": True,
        "img_url": img_url,
        "download_url": download_url,
        "title": parsed.get("title", ""),
        "summary": parsed.get("summary", ""),
        "points": parsed.get("points", [])[:5],
        "footer": parsed.get("footer", "")
    })


@bp.route("/health")
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "yitududong"})
