#!/usr/bin/env python3
"""
微信公众号草稿发布脚本 —— 直接调用微信官方 API，不经过任何第三方。
用法:
    python wechat_draft.py <html文件路径> [--title 标题] [--author 作者] [--cover 封面图路径]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 按优先级查找 .env: 1) 当前工作目录  2) 脚本所在目录的上级（scripts/→项目根）
def _find_env():
    cwd = Path.cwd() / ".env"
    if cwd.exists():
        return cwd
    sibling = Path(__file__).resolve().parent.parent / ".env"
    if sibling.exists():
        return sibling
    # 默认返回当前工作目录（后续会报错提示用户）
    return cwd

ENV_PATH = _find_env()


# ── 环境变量加载 ──────────────────────────────────────────────
def load_env():
    """从 .env 文件加载配置到 os.environ，不覆盖已存在的环境变量"""
    if not ENV_PATH.exists():
        print(f"[错误] 未找到 .env 文件: {ENV_PATH}")
        print(f"[提示] 请参考 .env.example 创建 .env 文件，填入你的 AppID 和 AppSecret")
        sys.exit(1)

    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


# ── 微信 API 调用 ──────────────────────────────────────────────
WECHAT_API_BASE = "https://api.weixin.qq.com"


def api_get(url: str) -> dict:
    """GET 请求微信 API，返回 JSON"""
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return json.loads(body) if body else {"errcode": e.code, "errmsg": str(e)}
    except URLError as e:
        return {"errcode": -1, "errmsg": str(e)}


def api_post(url: str, data: dict) -> dict:
    """POST JSON 请求微信 API"""
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return json.loads(body) if body else {"errcode": e.code, "errmsg": str(e)}
    except URLError as e:
        return {"errcode": -1, "errmsg": str(e)}


def api_post_file(url: str, file_path: str, file_field: str = "media") -> dict:
    """上传文件到微信 API (multipart/form-data)"""
    import email.generator as email_gen
    from io import BytesIO

    boundary = f"----WechatUpload{int(time.time())}"

    # 手动构造 multipart body（避免第三方依赖）
    body_parts = []
    # 文件字段
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "image/png"

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_data = f.read()

    body_parts.append(f"--{boundary}".encode("utf-8"))
    body_parts.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"'.encode("utf-8")
    )
    body_parts.append(f"Content-Type: {mime_type}".encode("utf-8"))
    body_parts.append(b"")
    body_parts.append(file_data)
    body_parts.append(f"--{boundary}--".encode("utf-8"))

    body = b"\r\n".join(body_parts)

    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return json.loads(body) if body else {"errcode": e.code, "errmsg": str(e)}
    except URLError as e:
        return {"errcode": -1, "errmsg": str(e)}


# ── 核心逻辑 ───────────────────────────────────────────────────

def get_access_token(appid: str, secret: str) -> str:
    """获取 access_token（仅在内存中，不写入任何文件）"""
    url = f"{WECHAT_API_BASE}/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    result = api_get(url)

    if "access_token" not in result:
        errcode = result.get("errcode", -1)
        errmsg = result.get("errmsg", "未知错误")
        print(f"[错误] 获取 access_token 失败: errcode={errcode}, errmsg={errmsg}")
        if errcode == 40013:
            print("[提示] AppID 无效，请检查 .env 中的 WECHAT_APPID")
        elif errcode == 40001:
            print("[提示] AppSecret 无效或过期，请检查")
        elif errcode == -1:
            print("[提示] 网络错误，无法连接微信服务器")
        sys.exit(1)

    token = result["access_token"]
    expires = result.get("expires_in", 0)
    print(f"[√] access_token 获取成功 (有效期 {expires} 秒)")
    return token


def upload_cover(token: str, cover_path: str) -> str:
    """上传封面图，返回 media_id"""
    url = f"{WECHAT_API_BASE}/cgi-bin/material/add_material?access_token={token}&type=image"
    result = api_post_file(url, cover_path)

    if "media_id" in result:
        print(f"[√] 封面图上传成功: media_id={result['media_id']}")
        return result["media_id"]
    else:
        print(f"[警告] 封面图上传失败: {result.get('errmsg', '未知错误')}")
        print("[提示] 将继续发布（无封面图）")
        return None


def create_draft(token: str, title: str, content: str, author: str = "",
                 digest: str = "", thumb_media_id: str = None) -> dict:
    """创建草稿"""
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/add?access_token={token}"

    article = {
        "title": title[:64],  # 微信限制 64 字符
        "content": content,
        "author": author[:8] if author else "",
        "digest": digest[:120] if digest else "",
        "content_source_url": "",
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }

    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id

    data = {"articles": [article]}
    result = api_post(url, data)

    if "media_id" in result:
        print(f"[√] 草稿创建成功！")
        print(f"    media_id: {result['media_id']}")
        return result
    else:
        print(f"[错误] 创建草稿失败: {result}")
        return result


def extract_html_content(html_path: str) -> str:
    """从 HTML 文件中提取正文内容（去除 <html><head><body> 等外层标签）"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 如果有 <body>，取 body 内容
    import re
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if body_match:
        return body_match.group(1).strip()

    # 否则去掉 html/head/doctype
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<html[^>]*>|</html>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<head>.*?</head>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html.strip()


def extract_title_from_html(html_path: str) -> str:
    """从 HTML 文件中提取标题"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    import re
    # 优先 <title>
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()

    # 其次 <h1>
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if h1_match:
        # 去掉内部的 span 标签
        text = re.sub(r"<[^>]+>", "", h1_match.group(1))
        return text.strip()

    return "未命名文章"


def extract_summary_from_html(html_path: str) -> str:
    """从 HTML 中提取第一段作为摘要"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    import re
    p_match = re.search(r"<p[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE)
    if p_match:
        text = re.sub(r"<[^>]+>", "", p_match.group(1))
        text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        return text.strip()[:120]
    return ""


# ── 主流程 ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="发布文章到微信公众号草稿箱 (直接调用微信官方 API)")
    parser.add_argument("html_file", help="HTML 文件路径")
    parser.add_argument("--title", "-t", help="文章标题 (默认从 HTML 提取)")
    parser.add_argument("--author", "-a", default="", help="作者名 (最多 8 字)")
    parser.add_argument("--cover", "-c", help="封面图路径 (本地文件)")
    parser.add_argument("--summary", "-s", help="文章摘要 (默认取第一段)")
    args = parser.parse_args()

    # 1. 加载配置
    load_env()
    appid = os.environ.get("WECHAT_APPID", "")
    secret = os.environ.get("WECHAT_APPSECRET", "")

    if not appid or not secret:
        print("[错误] WECHAT_APPID 或 WECHAT_APPSECRET 未在 .env 中配置")
        sys.exit(1)

    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"[错误] 文件不存在: {html_path}")
        sys.exit(1)

    print(f"→ 发布文章: {html_path.name}")
    print(f"→ 公众号 AppID: {appid[:6]}...{appid[-4:]}")
    print()

    # 2. 获取 access_token
    token = get_access_token(appid, secret)

    # 3. 提取标题和摘要
    title = args.title or extract_title_from_html(str(html_path))
    summary = args.summary or extract_summary_from_html(str(html_path))
    print(f"[i] 标题: {title}")
    print(f"[i] 摘要: {summary[:50]}...")

    # 4. 上传封面图 (如果有)
    thumb_media_id = None
    if args.cover:
        cover_path = Path(args.cover)
        if cover_path.exists():
            thumb_media_id = upload_cover(token, str(cover_path))
        else:
            print(f"[警告] 封面图不存在: {args.cover}")

    # 5. 读取 HTML 内容
    content = extract_html_content(str(html_path))
    print(f"[i] HTML 内容长度: {len(content)} 字符")

    # 6. 创建草稿
    print()
    result = create_draft(
        token=token,
        title=title,
        content=content,
        author=args.author,
        digest=summary,
        thumb_media_id=thumb_media_id,
    )

    if result.get("media_id"):
        print()
        print("═" * 50)
        print("  草稿已创建，请登录微信公众平台预览并发布")
        print("  https://mp.weixin.qq.com")
        print("═" * 50)
    else:
        print()
        print(f"[失败] {json.dumps(result, ensure_ascii=False)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
