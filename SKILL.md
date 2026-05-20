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

## Full Workflow

```
1. 撰写 → Markdown 文章（参考下方写作指南）
2. 转换 → npx md2wechat convert "article.md" "article.html"
3. 美化 → 按 HTML 格式化标准手动调优（配色/间距/引文样式）
4. 配图 → python scripts/generate_cover.py --title "..." --theme zen
5. 发布 → python scripts/wechat_draft.py article.html --cover cover.png
6. 预览 → mp.weixin.qq.com → 草稿箱 → 预览 → 发布
```

---

## Article Writing Guide（防 AI 味写作指南）

这些规则来自实际优化经验，目标是让文章读起来像**真人在分享体验**，而不是 AI 在输出知识。

### ✅ DO — 应该做的

| 原则 | 说明 | 示例 |
|------|------|------|
| **具体场景代替抽象概念** | 不说"信息焦虑"，说"凌晨三点还在刷手机" | ✓ "加班到很晚，关了电脑，心里空落落的" |
| **第一人称体验** | 用"我"的真实经历开头，而不是宏大叙事 | ✓ "第一次读《心经》，我20岁" |
| **短段落** | 一句话一段也行，比三句挤一起强 | ✓ 手机端阅读，段落越短越友好 |
| **对话感** | 像在跟朋友聊天，而不是在讲课 | ✓ "后来发现刚好相反" > "然而事实恰恰相反" |
| **收尾克制** | 说完就停，不要上价值不要升华 | ✓ "感谢读完。" > 长长一段"总结全文+互动引导" |

### ❌ DON'T — 避免的写法

| 坑 | 特征 | 改法 |
|----|------|------|
| **模板化开头** | "XX岁那年""最近XX刷屏了" | 换成具体事件，哪怕很小 |
| **编号流水账** | 1-2-3-4-5-6 结构化罗列 | 控制在 3-4 段，用标题代替编号 |
| **AI 腔词汇** | "心智操作系统""底层逻辑""核心方法论" | 用大白话重说一遍 |
| **三连举例** | "信息焦虑/职场倦怠/关系消耗" | 挑一个讲透，比列三个强 |
| **公式化结尾** | "欢迎在评论区聊聊"+"点个「在看」" | 直接删掉，或最多一个"感谢读完" |
| **强行升华** | 最后一段一定要上价值 | 停在最有力量那句话上 |

### 篇幅控制
- 公众号最优阅读长度：**1000-2000 字**正文
- 分段：每段不超过 3 句话，多换行
- 引用经文/名言用 `>` 单独成段，视觉上透气

---

## HTML Formatting Standards（HTML 格式规范）

md2wechat 生成的 HTML 有默认样式，但需要手动调优以下内容：

### 配色体系

| 主题 | 底色 | 主文字 | 强调色 | 适用 |
|------|------|--------|--------|------|
| **literary** (文学) | `#161720` 墨黑 | `#EEE` 米白 | `#FF9500` 暖橙 | 深度书评、思想类 |
| **zen** (禅意) | `#1A1A23` 墨紫 | `#3A3A3A` 炭灰 | `#8B7355` 暖棕金 | 佛学、哲学、心灵 |
| **tech** (科技) | `#0D1117` 暗蓝 | `#C9D1D9` 浅灰 | `#58A6FF` 蓝 | 技术、工具 |

### 排版参数

```css
/* 关键参数 — 直接改 HTML inline style */
font-size: 15px;          /* 正文字号（不用 16px，太密） */
line-height: 1.8;         /* 行高（不低 1.6） */
letter-spacing: 0.5px;    /* 字间距 */
color: #3a3a3a;           /* 正文颜色（不用纯黑 #000） */
```

### 标题
- **不保留编号**：md2wechat 自动编号的 `<span class="prefix">` 如果和内容重复要删
- **居中更禅意**：`text-align: center` + `letter-spacing: 1px`
- **不用粗底边**：用空行呼吸代替装饰线

### 分隔线
- 不用全宽黑线 `<hr>` — 太粗暴
- 用短金线：`width: 60px; margin: 0 auto; border-top: 1px solid #d4c5a0`

### 引文 blockquote
```html
<blockquote style="
  border-left: 2px solid #d4c5a0;
  background: rgba(180,160,120,0.06);
  padding: 14px 20px;
  border-radius: 0 4px 4px 0;
  margin: 0;
">
```

### 常见 md2wechat 坑
1. `<section>` 标签包裹 `<li>` — 无害但多余，可保留
2. `<span class="prefix">` 自动编号 — 如果 MD 标题本身无编号则保留，有则删除
3. `rgb(1,1,1)` 颜色值 — 直接改成 `#2c2c2c`

---

## Cover Design System（封面设计系统）

### 设计原则
- **留白为王**：文字不要填满，呼吸感 > 信息量
- **一个主视觉**：円相/书脊/几何图形，不要散
- **配色一致**：文章正文的强调色 = 封面强调色
- **字体考究**：楷体/仿宋 > 黑体/雅黑（文学类）

### 主题模板

| 主题 | 色盘 | 视觉元素 | 字体 |
|------|------|----------|------|
| **zen** | 墨紫 `#16151C` + 暖金 `#C6A046` + 米白 `#EBE6DA` | 円相（不闭合禅圆）、水墨晕染、竖金线 | 华文楷体 |
| **literary** | 墨黑 `#161720` + 暖橙 `#FF9500` + 冷白 `#EEE` | 书脊竖条、半透明叠层矩形 | 华文楷体 |
| **clean** | 纯黑 `#0A0A0A` + 白 `#FFF` | 几何线条、留白 | 华文中宋 |

### 生成命令

```bash
# 参数化生成（v3）
python scripts/generate_cover.py \
  --title "《心经》260字" \
  --subtitle "读了一辈子才明白" \
  --highlight "放下，即是拥有" \
  --theme zen \
  --output "cover.png"

# 或直接编辑脚本内的 create_cover() 定制
```

---

## Quality Checklist（发布前检查清单）

发布前逐项检查：

### 文章内容
- [ ] 开头是具体故事/场景，不是抽象论断
- [ ] 全文无 "心智操作系统""底层逻辑""核心方法论" 等 AI 腔词汇
- [ ] 段落短，手机屏 1-2 段/屏
- [ ] 结尾停在有力的话上，无公式化 CTA
- [ ] 字数 1000-2000（标题除外）

### HTML 格式
- [ ] 正文 15px / line-height 1.8 / color #3a3a3a
- [ ] h2 无重复编号，配色与封面一致
- [ ] 分隔线为短金线，非全宽黑线
- [ ] 引文左侧有细色线 + 淡色背景
- [ ] 无 `rgb(1,1,1)` 颜色值

### 封面
- [ ] 900×500px PNG
- [ ] 配色与文章 h2 强调色一致
- [ ] 主文字清晰可读（手机缩略图尺度）
- [ ] 有留白，不拥挤

### 发布
- [ ] .env 存在且连通（errcode=0）
- [ ] `--cover` 参数指向封面文件
- [ ] 标题 ≤ 64 字符
- [ ] mp.weixin.qq.com 草稿箱确认

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
