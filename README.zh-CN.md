<div align="center">

[![Resume Matcher](assets/header.png)](https://www.resumematcher.fyi)

# Resume Matcher

[English](README.md) | [Español](README.es.md) | **简体中文** | [日本語](README.ja.md)

### *[Resume Matcher](https://github.com/srbhr/Resume-Matcher) 的多租户 fork*

[𝙶𝚒𝚝𝙷𝚞𝚋](https://github.com/icemc/Resume-Matcher) ✦ [𝙳𝚘𝚌𝚔𝚎𝚛 𝙷𝚞𝚋](https://hub.docker.com/r/abanda/resume-matcher) ✦ [如何安装](#how-to-install) ✦ [𝙸𝚜𝚜𝚞𝚎𝚜](https://github.com/icemc/Resume-Matcher/issues) ✦ [原始项目](#original-project--attribution)

为每一次求职投递生成量身定制的简历：AI 给出可执行的优化建议。支持本地使用 Ollama 运行，也可通过 API 连接你常用的 LLM 提供商。

![Resume Matcher Demo](assets/Resume_Matcher_Demo_2.gif)

*（简历定制核心流程，继承自原始项目）*

</div>

<br>

<div align="center">

![Stars](https://img.shields.io/github/stars/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8)
![Apache 2.0](https://img.shields.io/github/license/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8) ![Forks](https://img.shields.io/github/forks/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8) ![version](https://img.shields.io/badge/Version-1.2.1--RC1-FFF?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-abanda%2Fresume--matcher-FFF?labelColor=F0F0E8&logo=docker&style=for-the-badge&color=1d4ed8)](https://hub.docker.com/r/abanda/resume-matcher)

</div>

> \[!IMPORTANT]
>
> **这是一个独立的 fork。** Resume Matcher 的核心产品——简历构建器、AI 定制、求职信、评分与模板——由 **[Saurabh Rai](https://github.com/srbhr)** 及 [原始 Resume Matcher](https://github.com/srbhr/Resume-Matcher) 社区设计和构建。本 fork 的目的是在此基础上增加**以语言为租户的多租户架构**（详见下方[本 fork 的新特性](#本-fork-的新特性)）。本项目与原团队没有从属、背书或维护关系。
>
> 如需**官方网站、最新动态、Discord 社区与赞助渠道**，请访问原始项目——见[原始项目与致谢](#original-project--attribution)。

## 本 fork 的新特性

现在，每种支持的语言都是独立的 **租户（tenant）**——拥有自己的 URL、自己的主简历、自己的定制简历，以及自己的求职跟踪看板，彼此完全隔离。租户之间唯一共享的是一个全局的界面语言设置。

| `/en/dashboard` | `/fr/dashboard` |
|---|---|
| ![英语租户仪表盘](assets/en-multi-tenant.png) | ![法语租户仪表盘](assets/fr-multi-tenant.png) |

- **按语言划分的独立仪表盘**：每种支持的语言（英语、西班牙语、中文、日语、葡萄牙语，以及本 fork 新增的**法语**）都有自己的 URL（`/en/dashboard`、`/fr/dashboard`、`/es/dashboard` 等）。
- **每个租户功能完全对等**——简历管理、定制、求职信、外联消息、AI 优化与求职跟踪，都在各自语言的独立工作区中运行。
- **顶部导航的租户切换器**会显示哪些语言已经配置（已有主简历），哪些尚未设置，并支持一键切换。
- **界面语言仍是全局设置**——界面语言（按钮、标签、导航）是所有租户共享的单一设置，与你当前所在的租户（内容语言）相互独立。
- 后端在数据层强制实施租户隔离：主简历按语言各设一份（而非全局唯一），所有列表/创建/上传类接口都要求显式指定租户。

完整技术说明见：[`docs/plans/language-tenant-dashboards.md`](docs/plans/language-tenant-dashboards.md)（英文）。

## 快速开始

Resume Matcher 的工作方式是先建立一份"主简历"，然后针对每个职位描述进行定制。安装说明见：[如何安装](#how-to-install)

### 工作流程

1. **上传**你的主简历（PDF 或 DOCX）
2. **粘贴**你要投递的职位描述（JD）
3. **审阅**AI 生成的改进建议与定制内容
4. **生成**该岗位的求职信
5. **自定义**版式与章节，匹配你的风格
6. **导出**为你选定模板的专业 PDF

以上每一步都在你当前所在的语言租户内进行——详见[本 fork 的新特性](#本-fork-的新特性)。

![Star Resume Matcher](assets/star_resume_matcher.png)

给 [本仓库](https://github.com/icemc/Resume-Matcher) 点 Star 来支持这个 fork，并及时获取新版本通知。

## 主要功能

![resume_matcher_features](assets/features.png)

### 核心能力

**主简历（Master Resume）**：基于你现有简历创建一份完整的主简历，后续每次投递都从这份主简历中抽取与定制。

![Job Description Input](assets/step_2_zh-CN.png)

### 简历生成器

![Resume Builder](assets/step_5_zh-CN.png)

粘贴职位描述后，获得针对该岗位定制的 AI 简历建议。

你可以：

- 修改建议内容
- 添加/移除章节
- 通过拖拽调整章节顺序
- 从多种简历模板中选择

### 求职信生成器

基于职位描述与你的简历，生成定制化的求职信。

![Cover Letter](assets/cover_letter_zh-CN.png)

### 简历评分与关键词高亮

对比你的简历与职位描述，输出匹配分数、关键词高亮与改进建议。

![Resume Scoring and Keyword Highlight](assets/keyword_highlighter_zh-CN.png)

### 求职跟踪看板

一个 7 列看板（已保存 → 已投递 → 未回复 → 已回复 → 面试 → 已录用 → 已拒绝），按语言租户隔离，用于跟踪每一次投递。

### PDF 导出

将定制后的简历与求职信导出为 PDF。

### 模板

| 模板名称 | 预览 | 说明 |
|---------|------|------|
| **经典单栏** | ![Classic Template](assets/pdf-templates/single-column.jpg) | 传统且干净的排版，适用于大多数行业。[查看 PDF](assets/pdf-templates/single-column.pdf) |
| **现代单栏** | ![Modern Template](assets/pdf-templates/modern-single-column.jpg) | 更强调可读性与审美的现代风格。[查看 PDF](assets/pdf-templates/modern-single-column.pdf) |
| **经典双栏** | ![Classic Two Column Template](assets/pdf-templates/two-column.jpg) | 将内容分区展示，更清晰易扫读。[查看 PDF](assets/pdf-templates/two-column.pdf) |
| **现代双栏** | ![Modern Two Column Template](assets/pdf-templates/modern-two-column.jpg) | 利用双栏结构做更强的信息组织。[查看 PDF](assets/pdf-templates/modern-two-column.pdf) |

### 国际化

- **多语言 UI**：界面支持英语、西班牙语、中文、日语、葡萄牙语（巴西）与法语——所有租户共享同一个全局设置。
- **按租户区分的多语言内容**：每个语言租户都会用自己的语言生成简历与求职信——详见[本 fork 的新特性](#本-fork-的新特性)。

### 路线图

如果你对本 fork 有建议或功能需求，欢迎[提交 Issue](https://github.com/icemc/Resume-Matcher/issues)。

- 用于打造量化、可落地简历内容的 AI 画布（AI Canvas）
- 面向求职投递的邮件模板生成器
- 多职位描述联合优化

<a id="how-to-install"></a>

## 如何安装

![Installation](assets/how_to_install_resumematcher.png)

更详细的安装与配置说明请查看 **[SETUP.zh-CN.md](SETUP.zh-CN.md)**。

### 前置条件

| 工具 | 版本 | 安装 |
|------|------|------|
| Python | 3.13+ | [python.org](https://python.org) |
| Node.js | 22+ | [nodejs.org](https://nodejs.org) |
| uv | 最新版 | [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |

### 快速开始

适用于 MacOS、WSL 与 Ubuntu 的最快方式：

```bash
# 克隆仓库
git clone https://github.com/icemc/Resume-Matcher.git
cd Resume-Matcher

# 后端（终端 1）
cd apps/backend
cp .env.example .env        # 配置你的 AI 提供商
uv sync                      # 安装依赖
uv run app

# 前端（终端 2）
cd apps/frontend
npm install
npm run dev
```

打开 **<http://localhost:3000>**，并在 Settings 中配置你的 AI 提供商。

### 支持的 AI 提供商

| 提供商 | 本地/云 | 说明 |
|--------|---------|------|
| **Ollama** | 本地 | 免费，在你的机器上运行 |
| **OpenAI** | 云 | GPT-5 Nano、GPT-4o |
| **Anthropic** | 云 | Claude Haiku 4.5 |
| **Google Gemini** | 云 | Gemini 3 Flash |
| **OpenRouter** | 云 | 访问多种模型 |
| **DeepSeek** | 云 | DeepSeek Chat |
| **OpenAI-Compatible** | 本地/云 | 任何暴露 OpenAI Chat Completions API 的服务（llama.cpp、vLLM、LM Studio、NVIDIA NIM 等） |

### Docker 部署

本 fork 的镜像已发布至 `linux/amd64` 与 `linux/arm64`：

- `ghcr.io/icemc/resume-matcher`
- `abanda/resume-matcher`

通过单一公开端口（`3000`）运行，API 位于 `/api`：

```bash
docker run --name resume-matcher \
  -p 3000:3000 \
  -v resume-data:/app/backend/data \
  abanda/resume-matcher:latest
```

生产环境建议固定版本，例如 `abanda/resume-matcher:v1.2.1-RC1`。

服务地址：

- 应用: <http://localhost:3000>
- API 健康检查: <http://localhost:3000/api/v1/health>
- API 文档: <http://localhost:3000/docs>

> **在 Docker 中使用 Ollama？** 将 Ollama URL 配置为 `http://host.docker.internal:11434`（而不是 `localhost`）。

### 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI、Python 3.13+、LiteLLM |
| 前端 | Next.js 16、React 19、TypeScript |
| 数据库 | SQLite（SQLAlchemy 2.0 async / aiosqlite） |
| 样式 | Tailwind CSS 4、Swiss International Style |
| PDF | Playwright 驱动的无头 Chromium |

## 参与贡献

![how to contribute](assets/how_to_contribute.png)

我们欢迎所有人为本 fork 做出贡献！无论你是开发者、设计师，还是希望帮忙的用户——欢迎在[本仓库](https://github.com/icemc/Resume-Matcher)提交 Issue 或 Pull Request。

如果你希望参与未来规划的功能，可以先看看路线图。贡献指南请参见 [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md)。

<a id="contributors"></a>

## 贡献者

<a href="https://github.com/icemc/Resume-Matcher/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=icemc/Resume-Matcher" />
</a>

<br/>

<details>
  <summary><kbd>Star 历史</kbd></summary>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=icemc/resume-matcher&theme=dark&type=Date">
    <img width="100%" src="https://api.star-history.com/svg?repos=icemc/resume-matcher&theme=dark&type=Date">
  </picture>
</details>

<a id="original-project--attribution"></a>

## 原始项目与致谢

本仓库是 **[Resume Matcher](https://github.com/srbhr/Resume-Matcher)** 的 fork，由 **Saurabh Rai**（[@srbhr](https://github.com/srbhr)）及其贡献者创建和维护。核心产品——简历解析、AI 定制、构建器、求职信、评分与模板——都是他们的成果。本 fork 在此基础上构建了多租户语言架构；上文描述的其余部分均属于原始项目。

我们目前还没有自己的网站、Discord 或社交媒体，因此以下内容请前往**原始项目**查看：

| | |
|---|---|
| 🌐 官网与实时演示 | [resumematcher.fyi](https://resumematcher.fyi) |
| 💬 Discord 社区 | [dsc.gg/resume-matcher](https://dsc.gg/resume-matcher) |
| 🐦 Twitter/X | [@srbhrai](https://twitter.com/srbhrai) |
| 💼 LinkedIn | [Resume Matcher](https://www.linkedin.com/company/resume-matcher/) |
| 👤 创作者 | [srbhr.com](https://srbhr.com) |

### 赞助

**请将任何赞助直接给予原始创作者，而非本 fork。** 是他们设计并构建了本 fork 所扩展的产品，理应获得你的支持：

| 平台  | 链接 |
|------|------|
| GitHub Sponsors | [github.com/sponsors/srbhr](https://github.com/sponsors/srbhr) |
| Buy Me a Coffee | [buymeacoffee.com/srbhr](https://www.buymeacoffee.com/srbhr) |

本 fork 不募集也不接受针对自身的赞助。

### 来自原始创作者

[![srbhr](assets/creators_note.png)](https://srbhr.com)

> 感谢您关注 Resume Matcher。如果您想联系、合作或只是打个招呼，请随时联系我！
> ~ **Saurabh Rai** ✨

- Website: [https://srbhr.com](https://srbhr.com)
- Linkedin: [https://www.linkedin.com/in/srbhr/](https://www.linkedin.com/in/srbhr/)
- Twitter: [https://twitter.com/srbhrai](https://twitter.com/srbhrai)
- GitHub: [https://github.com/srbhr](https://github.com/srbhr)
