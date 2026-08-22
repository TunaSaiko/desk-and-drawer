[English](README.md) ｜ [简体中文](README.zh.md) ｜ **日本語**

# desk-and-drawer

**机の上には今やっている仕事だけ。終わった仕事は引き出しへ。** AI エージェント協働プロジェクトの「正」となる markdown ドキュメント（進捗ボード・意思決定台帳）が際限なく肥大化するのを止めるガバナンス・キットです：方法論＋サイズゲート＋スターターテンプレート＋移行マニュアル。

## これは何か

Claude Code / Codex / Cursor などで長期間 AI 協働を回すプロジェクトには、進捗ボードや意思決定台帳といった「正」のドキュメントが育っていきます。**「書き方のルール」だけあって「アーカイブのルール」がないドキュメントは、必ず際限なく伸びます**——最後には read や grep が触れただけでエージェントのコンテキストウィンドウが吹き飛び、引き継ぎのたびに新しいエージェントが同じ税金を払うことになります。

本リポジトリはその処方箋です。すべて人間が読める git ネイティブな markdown のまま：

- 方法論：[`PLAYBOOK.md`](PLAYBOOK.md)——机/引き出しのアーキテクチャと、必経アクションに結び付けた五つのルール（現在は中国語、翻訳予定）
- スクリプト二つ：[`tools/check_doc_size.py`](tools/check_doc_size.py)（サイズゲート——**赤＝ローテーションの唯一のトリガー**）、[`tools/build_decisions_index.py`](tools/build_decisions_index.py)（台帳インデックスの機械生成、決定的出力）
- スターターテンプレート四つ：[`templates/`](templates/)——意思決定台帳／進捗ボード／エージェント入口ドキュメント／アーカイブディレクトリ
- 移行マニュアル：[`MIGRATION.md`](MIGRATION.md)——すでに肥大化したプロジェクト向け、コピペで使える保存則アサーション付き（現在は中国語）

## これは何でないか（関連プロジェクト）

正直に言うと、**これは発明ではなく、確立された実践の組み合わせ**です（ログローテーション、ADR、追記専用台帳、サイズ上限）。埋めた空白は「アーカイブのライフサイクルを、実行可能な規律としてパッケージした人がいなかった」ことです。

| プロジェクト | やること | 本キットとの関係 |
|---|---|---|
| [Beads](https://github.com/steveyegge/beads) | markdown のタスク管理を git 内蔵データベースに置き換える | 別レーン：あちらはストレージを替える、こちらは markdown のままナラティブ文書を統治する。競合ではなく補完 |
| [ctxlint](https://github.com/YawLabs/ctxlint) | CLAUDE.md / AGENTS.md を実コードベースと突き合わせて lint | 隣接：あちらはコンテキストファイルのドリフト対策、こちらは正文書のライフサイクル |
| [agents-md](https://github.com/ivawzh/agents-md) | AGENTS.md の分割合成＋CI サイズ制限 | 隣接：同じサイズゲート発想を、エージェント指示ファイルに適用 |
| [AgentLinter](https://agentlinter.com/) | CLAUDE.md の採点・診断 | 隣接：内容品質の lint、履歴アーカイブは対象外 |
| [memory-trail](https://github.com/frmoretto/memory-trail) | 決定メモリ＋セッションログ | 隣接：「なぜ」を記録する、ローテーション機構はなし |
| ADR（Architecture Decision Records） | 一決定一ファイル＋インデックス | 本キットの台帳パターンの源流のひとつ |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 仕様駆動開発：Propose → Apply → **Archive** | その Archive 工程は本キットの「終わったらアーカイブ」と同根 |

上流のアイデア：Anthropic「[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)」；OpenAI Codex がプロジェクト文書に課す 32KiB のハード上限（自覚に頼らずツールで強制する——本キットのゲートが受け継いだ態度です）。

## クイックスタート（新規プロジェクト初日）

1. `templates/docs/` をあなたのリポジトリへコピー——意思決定台帳／進捗ボード／**エージェント入口ドキュメント `HANDOFF.md`**／アーカイブディレクトリが揃います。
2. `tools/` の二つのスクリプトをコピーし、`check_doc_size.py` 冒頭の `CONFIG`（ファイル名＋バジェット。バジェット＝実測サイズ × 1.5–2.5）を書き換えてから、`python3 tools/build_decisions_index.py` を一度実行してインデックスを生成。
3. `docs/HANDOFF.md` をコメントに沿って穴埋め。エージェントが CLAUDE.md / AGENTS.md を使うなら、その中の「固定読み順＋必須ゲート」の節をそちらへ転記。
4. 最初の決定からルールを守る：一決定一行・番号は連番・追記専用（append-only）。
5. ゲートが赤になったら、赤字の処方どおりにローテーション——**バジェットを上げて誤魔化さない**。

すでに肥大化したプロジェクト → [`MIGRATION.md`](MIGRATION.md) へ。

## 日常への組み込み（規律は必経アクションに載せる）

- **エージェント側**：入口ドキュメントのテンプレートには必須ゲートが最初から入っています——新しいセッションは引き継ぎの第一歩で必ず実行します。
- **人間側**：コミット時に強制したいなら pre-commit フックを一つ：

  ```bash
  printf '#!/bin/sh\npython3 tools/check_doc_size.py || exit 1\n' > .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
  ```

- **CI 側**：スクリプトは標準ライブラリのみ・終了コード 0/1——どの CI でも `python3 tools/check_doc_size.py` の一行で必須チェックになります。

## 実戦の数字（出どころ：開始 7 週の非公開 iOS プロジェクト）

Before：進捗ボード 663KB / 1,763 行、意思決定台帳 819KB（274 件が一枚のテーブルに密集）、**最太の一行は 76,234 バイト**——read や grep が触れた瞬間、エージェントのコンテキストウィンドウが吹き飛ぶ状態。After：live ボード 237KB / 569 行、台帳 112KB（直近 30 件）、最長行 1,688 文字、**履歴の損失ゼロ**（移行スクリプトのアサーションで証明：改行除去後の再結合が sha256 で原文一致／決定番号 1..274 連番・欠落重複なし／タスク行 118 = アーカイブ 109 ＋ 保持 9）。全 6 コミット、各ステップ間で全ゲート緑を確認してから前進。

## FAQ

**Q: Beads を使えばよいのでは？** 新規プロジェクトなら大いにあり（PLAYBOOK §四）。本キットを選ぶ理由はだいたい次のどれかです：プロダクトオーナーが **markdown を直接読んで**プロジェクトを把握したい／バイナリ依存を増やしたくない／既存の markdown 資産が多く、途中でストレージを替えたくない。

**Q: プロジェクトに fork した後は、どちらが正？** プロジェクト内のルール文書が正です。本リポジトリは上流テンプレート。fork 後の分岐は正常な進化であり、還流は不要です。

## License

MIT © 2026 TunaSaiko
