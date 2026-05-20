---
name: wechat-official-draft-publisher
description: Publish Markdown/HTML articles to WeChat Official Account (微信公众号) draft box via official WeChat API — no third-party services, AppSecret stays local. Use when user wants to publish to WeChat drafts, push articles to 公众号草稿箱, mentions 发布到公众号, or needs to create WeChat drafts with cover images. Do NOT use for reading/extracting WeChat articles (use wechat-article-extractor instead).
---

# WeChat Official Draft Publisher

Publish articles directly to WeChat Official Account drafts via the **official WeChat API** — zero third-party services, AppSecret never leaves the machine.

## Prerequisites

- Python 3.9+ with Pillow: `pip install Pillow`
- WeChat Official Account (订阅号 or 服务号) with AppID and AppSecret
- Server IP added to IP whitelist in WeChat backend (开发 → 基本配置 → IP白名单)

## Configuration

### Step 1: Create `.env` file

Copy `assets/.env.example` to the project root as `.env`:

```
WECHAT_APPID=wx你的AppID
WECHAT_APPSECRET=你的AppSecret
```

**Security**: `.env` should be in `.gitignore`. AppSecret is read once at startup and never written to disk or transmitted to third parties.

### Step 2: Add IP to WeChat Whitelist

Log into [mp.weixin.qq.com](https://mp.weixin.qq.com), go to 开发 → 基本配置 → IP白名单, add the server's public IP.

To find your current public IP, run:

```bash
curl ifconfig.me
```

## Usage

### Quick Start (HTML file)

```bash
python scripts/wechat_draft.py "article.html" \
  --title "文章标题" \
  --author "作者名" \
  --cover "cover.jpg"
```

### Full Options

```bash
python scripts/wechat_draft.py <html_or_md_file> \
  [--title "标题"]      # Default: extracted from HTML <title> or <h1>
  [--author "作者"]     # Max 8 characters
  [--cover "path.jpg"]  # Local cover image, will be auto-uploaded
  [--summary "摘要"]    # Default: first paragraph of article
```

### Generate Cover Image

If no cover image is available, use the bundled cover generator:

```bash
python scripts/generate_cover.py
```

Edit the script to customize title, subtitle, colors, and layout. The generated image is 900×500px (WeChat recommended size).

## Workflow

```
1. Write article in Markdown → convert to HTML (e.g. with md2wechat)
2. Generate or prepare cover image (900×500px recommended)
3. Run: python scripts/wechat_draft.py article.html --cover cover.jpg
4. Log into mp.weixin.qq.com → 草稿箱 → preview → publish
```

## Security Design

| Feature | Detail |
|---------|--------|
| **Zero third-party** | Only `api.weixin.qq.com` is called |
| **Zero dependencies** | Python standard library only (except Pillow for cover generator) |
| **Secret in memory only** | AppSecret read once from `.env`, `access_token` never written to disk |
| **No data exfiltration** | No telemetry, no analytics, no external logging |
| **Auditable** | ~500 lines of readable Python, fully transparent |

## How It Works

1. `load_env()` reads AppID/AppSecret from `.env` into environment
2. `get_access_token()` calls `https://api.weixin.qq.com/cgi-bin/token`
3. `upload_cover()` uploads cover image to WeChat permanent materials
4. `extract_html_content()` strips outer HTML tags for clean content
5. `create_draft()` calls `https://api.weixin.qq.com/cgi-bin/draft/add`
6. Result: article appears in WeChat draft box, ready for manual review and publish

All API calls are to `api.weixin.qq.com` only. Nothing goes through wx.limyai.com or any other proxy.

## Troubleshooting

### `errcode: 40164, invalid ip`

**Cause**: Server IP not in WeChat whitelist.

**Fix**: Add the IP to 开发 → 基本配置 → IP白名单 in mp.weixin.qq.com.

### `errcode: 40007, invalid media_id`

**Cause**: Draft API requires `thumb_media_id` (cover image). You're publishing without `--cover`.

**Fix**: Provide a cover image with `--cover` flag, or run `scripts/generate_cover.py` to create one.

### `errcode: 40001, invalid credential`

**Cause**: AppSecret is wrong or expired.

**Fix**: Check `.env` file, verify AppSecret in mp.weixin.qq.com → 开发 → 基本配置.

### `errcode: 40013, invalid appid`

**Cause**: AppID is wrong.

**Fix**: Check `.env` file, verify AppID.

### `.env` file not found

**Cause**: The script looks for `.env` in the project root (parent of the `scripts/` directory).

**Fix**: Copy `assets/.env.example` to your project root as `.env` and fill in credentials.

## Limitations

- **Draft only**: Articles go to draft box, not directly published. Manual review and publish in mp.weixin.qq.com is required.
- **Title limit**: 64 characters (WeChat enforced)
- **Author limit**: 8 characters
- **Digest limit**: 120 characters
- **Cover image**: Must be a local file; script uploads it as permanent material to WeChat
- **No image-in-content upload**: Images embedded in HTML must use public URLs (they won't be auto-uploaded from local paths)
