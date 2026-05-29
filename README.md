# wechat-official-draft-publisher

> 微信公众号草稿发布 Skill / WeChat Official Account Draft Publisher — 纯官方 API，零第三方，安全透明。支持封面图生成、防 AI 味写作指南、公众号排版规范。

将 Markdown/HTML 文章一键发布到微信公众号草稿箱，全程只调 `api.weixin.qq.com`，AppSecret 不离开本机。适用于公众号写作、微信文章排版、自媒体内容创作。

## 特性

- **零第三方**：不经过任何代理/中间服务，直达微信官方 API
- **零依赖**：Python 标准库（封面生成仅需 Pillow）
- **安全透明**：~500 行可审计代码，access_token 仅存内存
- **配图生成**：内置参数化封面生成器，3 种主题（禅意/文学/极简）
- **写作指南**：内置防 AI 味写作规范 + 发布前质量 Checklist

## 快速开始

### 1. 安装

```bash
npx skills add stonebb/wechat-skills
```

### 2. 配置

在项目根目录创建 `.env`：

```
WECHAT_APPID=wx你的AppID
WECHAT_APPSECRET=你的AppSecret
```

将服务器 IP 加入微信公众号后台 **IP 白名单**（开发 → 基本配置）。

### 3. 使用

```bash
# 生成封面
python scripts/generate_cover.py \
  --theme zen \
  --title "《心经》260字" \
  --highlight "放下，即是拥有" \
  -o cover.png

# 发布到草稿箱
python scripts/wechat_draft.py article.html \
  --title "文章标题" \
  --cover cover.png
```

## 工作流

```
撰写 MD → md2wechat 转 HTML → 手动调样式 → 生成封面 → 发布草稿
   ↑ 参照写作指南    ↑ 参照格式规范   ↑ 参数化脚本   ↑ 一键命令
```

## 文件结构

```
wechat-official-draft-publisher/
├── SKILL.md                      # Skill 定义（写作指南、格式规范、Checklist）
├── README.md
├── scripts/
│   ├── wechat_draft.py           # 核心发布脚本
│   └── generate_cover.py         # 参数化封面生成器
└── assets/
    └── .env.example              # 配置模板
```

## 封面主题

| 主题 | 配色 | 视觉元素 | 适用 |
|------|------|----------|------|
| `zen` | 墨紫 + 暖金 + 米白 | 円相、水墨晕染 | 佛学、哲学、心灵 |
| `literary` | 墨黑 + 暖橙 + 冷白 | 书脊竖条、半透明叠层 | 深度书评、思想类 |
| `clean` | 纯黑 + 白 | 几何线条 | 技术、工具 |

## 安全设计

- 只调用 `api.weixin.qq.com`，不经过任何代理
- AppSecret 读取后仅在内存中，不写入任何文件
- access_token 不落盘，无日志泄露风险
- 无遥测、无统计、无外部日志

## 常见问题

| 错误 | 原因 | 解决 |
|------|------|------|
| `errcode 40164` | IP 不在白名单 | 公众号后台添加 IP |
| `errcode 40007` | 缺少封面图 | 加 `--cover` 参数 |
| `errcode 40001` | AppSecret 错误 | 检查 `.env` |
| `.env` 找不到 | 路径问题 | 放在项目根目录或 `scripts/` 上级 |

## License

MIT
