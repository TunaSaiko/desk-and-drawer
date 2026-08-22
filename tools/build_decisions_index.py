#!/usr/bin/env python3
"""重建决策账本的一行一条快速索引（通用版）。方法论见 PLAYBOOK.md §三-3。

**索引是 derived 文件，不是权威**：权威永远是账本正文（live ＋ 归档段）。
生成是确定性的（同输入必同输出、不带时间戳），所以 check_doc_size.py 可以用
「重新生成 == 落盘内容」当新鲜度判据；索引过期的修法就是重跑本脚本。

摘要取法：整行去掉表格前两格（编号/日期）后，剥掉 `**`/反引号再截前 90 字。
刻意不按单元格切——含转义竖线 \\| 的行按格切会切坏；剥反引号是防旧 commit
SHA 之类的串进索引后触发别的扫描器。截断可能带进下一列开头几个字，不影响
索引用途（找到条目后回正文读原文）。
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============ 按你的项目改这里（须与 check_doc_size.py 的 ledger 配置一致） ============
LIVE = "docs/DECISIONS.md"
ARCHIVE_GLOB = "docs/archive/DECISIONS-D*.md"
ROW_REGEX = r"^\| D(\d+) \| (\d{2}-\d{2}) \| (.*)\|\s*$"
OUT = "docs/DECISIONS-INDEX.md"
WIDTH = 90
# ====================================================================


def collect():
    paths = sorted(glob.glob(os.path.join(ROOT, ARCHIVE_GLOB)))
    paths.append(os.path.join(ROOT, LIVE))
    rows = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        for l in open(p, encoding="utf-8").read().split("\n"):
            m = re.match(ROW_REGEX, l)
            if m:
                n = int(m.group(1))
                assert n not in rows, "D%d 在多处出现（live 与归档重复？）" % n
                rows[n] = (m.group(2), m.group(3))
    return rows


def build():
    rows = collect()
    assert rows and sorted(rows) == list(range(1, max(rows) + 1)), "决策号不连续，先查账本再建索引"
    out = [
        "# 决策快速索引（derived · 机械生成 · 不是权威）",
        "",
        "> 由 `python3 tools/build_decisions_index.py` 从账本 live＋归档段全量重建。",
        "> 索引过期时 check_doc_size.py 会报红，修法＝重跑上面那条命令。查到条目后请回正文读原文——摘要是截断的。",
        "",
    ]
    for n in sorted(rows):
        date, rest = rows[n]
        s = re.sub(r"[`*]", "", rest).strip()
        s = s[:WIDTH] + ("…" if len(s) > WIDTH else "")
        out.append("- D%d ｜%s｜ %s" % (n, date, s))
    out.append("")
    return "\n".join(out)


def main():
    text = build()
    open(os.path.join(ROOT, OUT), "w", encoding="utf-8").write(text)
    print("✅ 索引已重建：%d 条 → %s" % (text.count("\n- D"), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
