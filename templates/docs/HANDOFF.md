# 接手入口（稳定版）

> 本文件是 AI agent 新会话的**固定入口**：只讲「怎么接手」，**不保存任何会过期的动态状态**。
> 当前状态的唯一权威 = `PROGRESS.md` ＋ Git。（用 CLAUDE.md / AGENTS.md 的项目：把下面两节抄进去即可。）

## 固定阅读顺序

1. `docs/PROGRESS.md` —— 当前状态唯一真相（阶段／任务表／待验／候选池／债务）
2. `docs/DECISIONS.md` —— 决策账本 live 段；**快查先看 `docs/DECISIONS-INDEX.md`**（derived 索引，非权威），老段档在 `docs/archive/DECISIONS-D*.md`
3. **历史流水一律在 `docs/archive/`——按需 grep、不通读**
4. （在这里补你项目自己的：产品文档／技术规格／当前任务书……）

## 接手第一步：先只读核对，后写入

1. Git 事实核对（不盲信任何交接摘要）：

   ```
   git status -s && git log --oneline -8
   ```

2. **必跑门禁**：

   ```
   python3 tools/check_doc_size.py     # 文档体积/单行长度/决策号连续/归档卫生/索引新鲜
   ```

   （把你项目自己的其他门禁也列在这里——门禁新增时**同一提交里更新本清单**，"门禁长出来了、名单没跟上"是高复发漂移。）

3. 先向用户报告观察到的状态，**报告之前不写、不 commit、不 push**。

## 写文档时的三条纪律（详见 PLAYBOOK）

- PROGRESS 头部状态行**整行替换、禁止行内续写**；被替换旧行追加 `docs/archive/PROGRESS-status-log.md`。
- 阶段收官／任务关账 → 对应内容移入 `docs/archive/`，原地留指针或区间行。
- 决策一条一行、编号连续、append-only；改主意＝新增条目注明取代关系。
