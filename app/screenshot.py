"""
长图生成器：使用 Playwright 将 HTML 渲染为高清 PNG
"""
import os
import uuid
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Playwright 浏览器实例（全局复用）
_browser = None
_playwright = None


def get_browser():
    global _browser, _playwright
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )
    return _browser


def render_html_to_screenshot(html_content, output_dir, width=1080):
    """
    将 HTML 内容渲染为 PNG 长图

    Args:
        html_content: HTML 字符串
        output_dir: 输出目录
        width: 截图宽度（像素）

    Returns:
        输出图片路径
    """
    browser = get_browser()
    page = browser.new_page(viewport={"width": width, "height": 800})

    # 设置内容
    page.set_content(html_content, wait_until="networkidle", timeout=30000)

    # 等待字体/图片加载
    try:
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # 生成文件名
    filename = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, filename)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 截图
    page.screenshot(
        path=output_path,
        type="png",
        full_page=True,
        timeout=30000
    )

    page.close()
    return output_path


def cleanup_old_outputs(output_dir, max_age_hours=24):
    """清理过期输出文件"""
    import time
    cutoff = time.time() - max_age_hours * 3600
    output_path = Path(output_dir)
    if not output_path.exists():
        return
    for f in output_path.glob("*.png"):
        if f.stat().st_mtime < cutoff:
            try:
                f.unlink()
            except Exception:
                pass
