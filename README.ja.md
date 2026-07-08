<div align="center">

[![Resume Matcher](assets/header.png)](https://www.resumematcher.fyi)

# Resume Matcher

[English](README.md) | [Español](README.es.md) | [简体中文](README.zh-CN.md) | **日本語**

### *[Resume Matcher](https://github.com/srbhr/Resume-Matcher) のマルチテナント fork*

[𝙶𝚒𝚝𝙷𝚞𝚋](https://github.com/icemc/Resume-Matcher) ✦ [𝙳𝚘𝚌𝚔𝚎𝚛 𝙷𝚞𝚋](https://hub.docker.com/r/abanda/resume-matcher) ✦ [𝙸𝚗𝚜𝚝𝚊𝚕𝚕 𝙼𝚎𝚝𝚑𝚘𝚍](#how-to-install) ✦ [𝙸𝚜𝚜𝚞𝚎𝚜](https://github.com/icemc/Resume-Matcher/issues) ✦ [𝙾𝚛𝚒𝚐𝚒𝚗𝚊𝚕 𝙿𝚛𝚘𝚓𝚎𝚌𝚝](#original-project--attribution)

求人ごとに最適化した履歴書を、AI の提案で作成できます。Ollama を使ってローカルで動かすことも、API 経由でお気に入りの LLM プロバイダに接続することも可能です。

![Resume Matcher Demo](assets/Resume_Matcher_Demo_2.gif)

*（履歴書最適化のコアフローは、オリジナルプロジェクトから継承しています）*

</div>

<br>

<div align="center">

![Stars](https://img.shields.io/github/stars/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8)
![Apache 2.0](https://img.shields.io/github/license/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8) ![Forks](https://img.shields.io/github/forks/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8) ![version](https://img.shields.io/badge/Version-1.2.1--RC1-FFF?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-abanda%2Fresume--matcher-FFF?labelColor=F0F0E8&logo=docker&style=for-the-badge&color=1d4ed8)](https://hub.docker.com/r/abanda/resume-matcher)

</div>

> \[!IMPORTANT]
>
> **これは独立した fork です。** 履歴書ビルダー、AI による最適化、カバーレター、スコアリング、テンプレートといった Resume Matcher のコア機能は、**[Saurabh Rai](https://github.com/srbhr)** 氏と [オリジナルの Resume Matcher](https://github.com/srbhr/Resume-Matcher) コミュニティによって設計・構築されたものです。この fork は、その成果の上に**言語をテナントとするマルチテナント・アーキテクチャ**を追加するために存在します（詳しくは下記の[この fork の新機能](#この-fork-の新機能)を参照）。オリジナルチームとの提携・承認・保守関係はありません。
>
> **公式サイト、最新情報、Discord コミュニティ、スポンサーシップ**については、オリジナルプロジェクトをご覧ください — [オリジナルプロジェクトとクレジット](#original-project--attribution) を参照してください。

## この fork の新機能

対応する各言語は、それぞれ独立した **テナント** になりました — 専用の URL、専用のマスター履歴書、専用の最適化済み履歴書、専用の応募トラッカーボードを持つ、完全に分離されたワークスペースです。テナント間で共有されるのは、グローバルな UI 言語設定だけです。

| `/en/dashboard` | `/fr/dashboard` |
|---|---|
| ![英語テナントのダッシュボード](assets/en-multi-tenant.png) | ![フランス語テナントのダッシュボード](assets/fr-multi-tenant.png) |

- **言語ごとの専用ダッシュボード**：対応する各言語（英語、スペイン語、中国語、日本語、ポルトガル語、そしてこの fork で新たに追加された**フランス語**）が、それぞれ専用の URL（`/en/dashboard`、`/fr/dashboard`、`/es/dashboard` など）を持ちます。
- **テナントごとの完全な機能パリティ** — 履歴書管理、最適化、カバーレター、アウトリーチ、AI による強化、トラッカーはすべて、各言語専用のワークスペース内で独立して動作します。
- **テナント切り替え**：上部ナビにあるスイッチャーで、どの言語がすでに設定済み（マスター履歴書がある）で、どれが未設定かが一目でわかり、ワンクリックで切り替えられます。
- **UI 言語はグローバルのまま** — インターフェースの言語（ボタン、ラベル、ナビゲーション）は、現在作業中のテナント（コンテンツ言語）とは別に、すべてのテナントで共有される 1 つのグローバル設定です。
- バックエンドはデータ層でテナントの分離を強制します：マスター履歴書はグローバルに 1 件ではなく、言語ごとに 1 件。すべての一覧取得／作成／アップロード系エンドポイントは明示的なテナント指定を必須とします。

技術的な詳細はこちら: [`docs/plans/language-tenant-dashboards.md`](docs/plans/language-tenant-dashboards.md)（英語）。

## はじめに

Resume Matcher は、まず「マスター履歴書」を作り、それを各求人応募向けに調整する形で動作します。インストール手順は：[インストール方法](#how-to-install)

### 仕組み

1. **アップロード**：マスター履歴書（PDF / DOCX）
2. **貼り付け**：応募先の求人票（Job Description）
3. **確認**：AI が生成した改善案と最適化内容
4. **生成**：求人向けのカバーレター
5. **調整**：レイアウトやセクションを好みに合わせてカスタマイズ
6. **書き出し**：好みのテンプレートで PDF を出力

上記の各ステップは、現在いるどの言語テナントの中でも同じように行えます — 詳しくは[この fork の新機能](#この-fork-の新機能)を参照してください。

![Star Resume Matcher](assets/star_resume_matcher.png)

[このリポジトリ](https://github.com/icemc/Resume-Matcher)に Star を付けていただけると、fork の開発の励みになります（リリース通知も受け取れます）。

## 主な機能

![resume_matcher_features](assets/features.png)

### コア機能

**マスター履歴書（Master Resume）**：既存の履歴書から、再利用できる包括的なマスター履歴書を作成します。

![Job Description Input](assets/step_2.png)

### 履歴書ビルダー

![Resume Builder](assets/step_5_ja.png)

求人票を貼り付けると、その職種に合わせた AI 提案の履歴書を生成します。

できること：

- 提案内容の編集
- セクションの追加/削除
- ドラッグ＆ドロップで順序変更
- 複数テンプレートから選択

### カバーレター生成

求人票と履歴書に基づき、カスタマイズされたカバーレターを生成します。

![Cover Letter](assets/cover_letter_ja.png)

### 履歴書スコアリング＆キーワードハイライト

履歴書と求人票を比較し、マッチスコア・キーワードハイライト・改善提案を表示します。

![Resume Scoring and Keyword Highlight](assets/keyword_highlighter_ja.png)

### 応募トラッカー

7 段階のカンバンボード（保存 → 応募済み → 未返信 → 返信あり → 面接 → 内定 → 不採用）で、各応募を言語テナントごとに管理できます。

### PDF 出力

最適化した履歴書とカバーレターを PDF として出力できます。

### テンプレート

| テンプレート名 | プレビュー | 説明 |
|---------------|-----------|------|
| **クラシック（1 カラム）** | ![Classic Template](assets/pdf-templates/single-column.jpg) | 伝統的でクリーンなレイアウト。多くの業種に適しています。[PDF を見る](assets/pdf-templates/single-column.pdf) |
| **モダン（1 カラム）** | ![Modern Template](assets/pdf-templates/modern-single-column.jpg) | 可読性と美しさを重視した現代的なデザイン。[PDF を見る](assets/pdf-templates/modern-single-column.pdf) |
| **クラシック（2 カラム）** | ![Classic Two Column Template](assets/pdf-templates/two-column.jpg) | セクションを分けて見やすく整理します。[PDF を見る](assets/pdf-templates/two-column.pdf) |
| **モダン（2 カラム）** | ![Modern Two Column Template](assets/pdf-templates/modern-two-column.jpg) | 2 カラムを活用して情報をより整理します。[PDF を見る](assets/pdf-templates/modern-two-column.pdf) |

### 国際化

- **多言語 UI**：英語・スペイン語・中国語・日本語・ポルトガル語（ブラジル）・フランス語に対応 — すべてのテナントで共有される 1 つのグローバル設定です。
- **テナントごとの多言語コンテンツ**：各言語テナントは、それぞれの言語で履歴書とカバーレターを生成します — 詳しくは[この fork の新機能](#この-fork-の新機能)を参照してください。

### ロードマップ

この fork への提案や機能要望があれば、[Issue を作成](https://github.com/icemc/Resume-Matcher/issues)してください。

- 定量的でインパクトのある内容を作る AI Canvas
- 求人応募向けのメールテンプレート生成機能
- 複数求人票の同時最適化

<a id="how-to-install"></a>

## インストール方法

![Installation](assets/how_to_install_resumematcher.png)

詳細なセットアップ手順は **[SETUP.ja.md](SETUP.ja.md)** を参照してください。

### 前提条件

| ツール | バージョン | インストール |
|--------|------------|--------------|
| Python | 3.13+ | [python.org](https://python.org) |
| Node.js | 22+ | [nodejs.org](https://nodejs.org) |
| uv | 最新 | [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |

### クイックスタート

MacOS / WSL / Ubuntu で最も手早い手順：

```bash
# リポジトリをクローン
git clone https://github.com/icemc/Resume-Matcher.git
cd Resume-Matcher

# バックエンド（ターミナル 1）
cd apps/backend
cp .env.example .env        # AI プロバイダを設定
uv sync                      # 依存関係をインストール
uv run app

# フロントエンド（ターミナル 2）
cd apps/frontend
npm install
npm run dev
```

**<http://localhost:3000>** を開き、Settings で AI プロバイダを設定してください。

### 対応 AI プロバイダ

| プロバイダ | ローカル/クラウド | 備考 |
|------------|-------------------|------|
| **Ollama** | ローカル | 無料。手元のマシンで動作 |
| **OpenAI** | クラウド | GPT-5 Nano、GPT-4o |
| **Anthropic** | クラウド | Claude Haiku 4.5 |
| **Google Gemini** | クラウド | Gemini 3 Flash |
| **OpenRouter** | クラウド | 複数モデルへアクセス |
| **DeepSeek** | クラウド | DeepSeek Chat |
| **OpenAI-Compatible** | ローカル/クラウド | OpenAI Chat Completions API 互換のサーバー（llama.cpp、vLLM、LM Studio、NVIDIA NIM など） |

### Docker デプロイ

この fork のイメージは `linux/amd64` と `linux/arm64` 向けに以下で公開しています：

- `ghcr.io/icemc/resume-matcher`
- `abanda/resume-matcher`

単一の公開ポート（`3000`）で起動し、API は `/api` で利用できます：

```bash
docker run --name resume-matcher \
  -p 3000:3000 \
  -v resume-data:/app/backend/data \
  abanda/resume-matcher:latest
```

本番環境ではバージョンを固定することを推奨します。例：`abanda/resume-matcher:v1.2.1-RC1`。

エンドポイント：

- アプリ本体: <http://localhost:3000>
- API ヘルスチェック: <http://localhost:3000/api/v1/health>
- API ドキュメント: <http://localhost:3000/docs>

> **Docker で Ollama を使う場合**：Ollama の URL は `localhost` ではなく `http://host.docker.internal:11434` を指定します。

### 技術スタック

| コンポーネント | 技術 |
|----------------|------|
| バックエンド | FastAPI、Python 3.13+、LiteLLM |
| フロントエンド | Next.js 16、React 19、TypeScript |
| データベース | SQLite（SQLAlchemy 2.0 async / aiosqlite） |
| スタイリング | Tailwind CSS 4、Swiss International Style |
| PDF | Playwright による Headless Chromium |

## 参加・コントリビュート

![how to contribute](assets/how_to_contribute.png)

この fork へのコントリビュートを歓迎します。開発者・デザイナー・ユーザーを問わず、協力してくれる方を募集しています — [このリポジトリ](https://github.com/icemc/Resume-Matcher)に Issue や Pull Request を作成してください。

計画中の機能に取り組みたい場合はロードマップをご覧ください。コントリビューションガイドは [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) を参照してください。

<a id="contributors"></a>

## コントリビューター

<a href="https://github.com/icemc/Resume-Matcher/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=icemc/Resume-Matcher" />
</a>

<br/>

<details>
  <summary><kbd>Star の推移</kbd></summary>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=icemc/resume-matcher&theme=dark&type=Date">
    <img width="100%" src="https://api.star-history.com/svg?repos=icemc/resume-matcher&theme=dark&type=Date">
  </picture>
</details>

<a id="original-project--attribution"></a>

## オリジナルプロジェクトとクレジット

このリポジトリは、**[Saurabh Rai](https://github.com/srbhr)** 氏（[@srbhr](https://github.com/srbhr)）とそのコントリビューターによって作られ、保守されている **[Resume Matcher](https://github.com/srbhr/Resume-Matcher)** の fork です。履歴書の解析、AI による最適化、ビルダー、カバーレター、スコアリング、テンプレートなど、コア機能はすべて彼らの成果です。この fork は、その上にマルチテナントの言語アーキテクチャを追加したものであり、それ以外の部分はすべてオリジナルプロジェクトに帰属します。

私たちはまだ独自のウェブサイトや Discord、SNS を持っていないため、以下についてはすべて **オリジナルプロジェクト** をご覧ください：

| | |
|---|---|
| 🌐 公式サイト・ライブプレビュー | [resumematcher.fyi](https://resumematcher.fyi) |
| 💬 Discord コミュニティ | [dsc.gg/resume-matcher](https://dsc.gg/resume-matcher) |
| 🐦 Twitter/X | [@srbhrai](https://twitter.com/srbhrai) |
| 💼 LinkedIn | [Resume Matcher](https://www.linkedin.com/company/resume-matcher/) |
| 👤 制作者 | [srbhr.com](https://srbhr.com) |

### スポンサーシップ

**スポンサーシップは、この fork ではなくオリジナルの制作者へお願いします。** この fork が拡張している製品を設計・構築したのは彼らであり、支援の恩恵を受けるべきなのも彼らです：

| プラットフォーム | リンク |
|------------------|--------|
| GitHub Sponsors | [github.com/sponsors/srbhr](https://github.com/sponsors/srbhr) |
| Buy Me a Coffee | [buymeacoffee.com/srbhr](https://www.buymeacoffee.com/srbhr) |

この fork は独自のスポンサーシップを募集・受け付けていません。

### オリジナルの制作者より

[![srbhr](assets/creators_note.png)](https://srbhr.com)

> Resume Matcher をご覧いただきありがとうございます。つながりやコラボレーション、あるいは挨拶だけでも、お気軽にご連絡ください！
> ~ **Saurabh Rai** ✨

- Website: [https://srbhr.com](https://srbhr.com)
- Linkedin: [https://www.linkedin.com/in/srbhr/](https://www.linkedin.com/in/srbhr/)
- Twitter: [https://twitter.com/srbhrai](https://twitter.com/srbhrai)
- GitHub: [https://github.com/srbhr](https://github.com/srbhr)
