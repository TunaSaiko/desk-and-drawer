[English](README.md) ｜ **简体中文** ｜ [日本語](README.ja.md)

# desk-and-drawer

**桌面上只放正在干的活，干完的活收进抽屉。** 一套让 AI 协作项目的权威 markdown 文档（进度看板、决策账本）不再无限变长的治理方案：方法论＋体积门禁＋起步模板＋迁移手册。

## 这是什么

长期跑 AI 协作（Claude Code / Codex / Cursor…）的项目，权威文档——进度看板、决策账本——**只要有"怎么记"的规则、没有"怎么归档"的规则，就必然无限变长**，最后把每一任接手 agent 的上下文窗顶爆。

本仓库是治这个病的一套**留在 markdown 里**的方案：

- 一份方法论：[`PLAYBOOK.md`](PLAYBOOK.md)（桌面/抽屉分工、五条绑在必经动作上的规矩）
- 两个脚本：[`tools/check_doc_size.py`](tools/check_doc_size.py)（体积门禁，**报红＝轮转的唯一触发**）、[`tools/build_decisions_index.py`](tools/build_decisions_index.py)（决策索引，机械生成、确定性输出）
- 四份起步模板：[`templates/`](templates/)（决策账本／进度看板／agent 入口文档／归档目录）
- 一份迁移手册：[`MIGRATION.md`](MIGRATION.md)（给已经长大的项目，含"只挪不改"的机械核数代码片段）

## 这不是什么（相关工作对照）

诚实声明：**这不是一个发明，是对既有实践的组合**（日志轮转、ADR、append-only 账本、体积上限），填的空档是"没人把归档生命周期打包成可执行的纪律"。相邻项目与本仓的分工：

| 项目 | 它做什么 | 与本仓的关系 |
|---|---|---|
| [Beads](https://github.com/steveyegge/beads) | 把任务追踪从 markdown 换成 git 内嵌数据库 | 不同赛道：它换存储，本仓留在 markdown 里治叙事文档；互补不竞争 |
| [ctxlint](https://github.com/YawLabs/ctxlint) | 对 CLAUDE.md/AGENTS.md 做"与代码库对不对得上"的 lint | 相邻：它治上下文文件的漂移，本仓治权威文档的生命周期 |
| [agents-md](https://github.com/ivawzh/agents-md) | AGENTS.md 分片组装＋CI 体积限制 | 相邻：同样用体积门禁思路，但对象是 agent 指令文件 |
| [AgentLinter](https://agentlinter.com/) | CLAUDE.md 评分/诊断 | 相邻：lint 内容质量，不管历史归档 |
| [memory-trail](https://github.com/frmoretto/memory-trail) | 决策记忆＋会话日志 | 相邻：记录"为什么"，无轮转机制 |
| ADR（架构决策记录） | 一决策一文件＋索引 | 本仓账本模式的思想来源之一 |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 规格驱动开发，Propose→Apply→**Archive** | 它的 Archive 环节与本仓"做完就归档"同源 |

理念上游：Anthropic《[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)》；OpenAI Codex 对项目说明文档的 32KiB 硬上限（工具强制、不信自觉——本仓门禁的态度来源）。

## 快速开始（新项目第一天）

1. 把 `templates/docs/` 复制进你的仓库——决策账本／进度看板／**入口文档 HANDOFF.md**／归档目录各就位。
2. 把 `tools/` 两个脚本复制过去，改 `check_doc_size.py` 顶部的 `CONFIG`（文件名＋预算；预算 = 实测体积 × 1.5–2.5），然后跑一次 `python3 tools/build_decisions_index.py` 生成索引。
3. 打开 `docs/HANDOFF.md` 按注释填空；如果你的 agent 用 CLAUDE.md / AGENTS.md，把里面那段「固定阅读顺序＋必跑门禁」抄进去。
4. 从第一条决策起就守规矩：一条一行、编号连续、append-only。
5. 门禁报红时照红字里的处方轮转——**不许调预算了事**。

已经长大的项目 → 直接看 [`MIGRATION.md`](MIGRATION.md)。

## 怎么绑进日常（纪律必须挂在必经动作上）

- **agent 侧**：入口文档的必跑清单里有门禁（模板已带）——每个新会话接手第一步就会跑。
- **人类侧**：想在提交时强制，加一个 pre-commit hook 即可：

  ```bash
  printf '#!/bin/sh\npython3 tools/check_doc_size.py || exit 1\n' > .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
  ```

- **CI 侧**：脚本退出码 0/1、无任何依赖（纯标准库），在任何 CI 里加一行 `python3 tools/check_doc_size.py` 就是一道必过检查。

## 实战数字（出处：一个跑了 7 周的私有 iOS 项目）

治理前：进度看板 663KB / 1,763 行，决策账本 819KB / 274 条挤一张表，**最粗的一行 76,234 字节**——任何读取或 grep 碰到它就把 agent 的上下文窗顶爆。治理后：live 看板 237KB / 569 行、账本 112KB（留最近 30 条），最长行 1,688 字符；**历史零丢失**（迁移脚本断言：内容拼接 sha256 与原文一致、决策号 1..274 连续无缺无重、任务行 118 = 归档 109 + 保留 9）。全程 6 个提交，每步之间全部门禁绿才推进。

## FAQ

**Q：为什么不直接用 Beads？** 新项目完全可以（见 PLAYBOOK §四）。选本仓的理由通常是：产品所有者要**直接读 markdown** 掌握项目、不想加二进制依赖、或项目已有大量 markdown 资产不宜中途换存储。

**Q：被 fork 进具体项目之后听谁的？** 听项目内的规则文档。本仓库是上游模板；fork 后的分歧属正常演化，不必回流。

## License

MIT © 2026 TunaSaiko
