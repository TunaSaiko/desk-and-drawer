#!/usr/bin/env python3
"""文档体积与归档生命周期门禁（通用版）。方法论见仓库根的 PLAYBOOK.md。

**报红 = 轮转的唯一触发**（PLAYBOOK §三-4：刻意单触发，避免"条数规则"与
"体积规则"两个触发器打架）。每条红都随文给处方；不许调预算了事——调预算
应在你的项目里走决策留痕。

查五项（按 CONFIG 配置，未配置的项跳过并明说）：
  ① 权威文档字节预算                       【硬错】
  ② 单行长度上限（防"行内续写"单行怪物）   【硬错】
  ③ 决策号完整性：live＋归档全集 1..max 连续无重【硬错】
  ④ 归档任务行卫生：行行已关账、无自相矛盾  【硬错】
  ⑤ 决策索引新鲜度：确定性重建 == 落盘内容  【硬错】

两条实测教训（PLAYBOOK §六）：
  - 预算按**字节**（os.path.getsize），行长按**字符**（Python len）——单位不同，
    报数字时说清（BSD awk length 数的是字节，别拿它对 Python len）。
  - "配置了但文件不存在"判红；"没配置"跳过；**全部跳过时大声说"没有任何
    检查生效"**——exit 0 不等于"已治理"。

用法：
  python3 tools/check_doc_size.py                # 0=通过 / 1=有硬错
  python3 tools/check_doc_size.py --self-test    # 纯判定的阳性+阴性校准
  python3 tools/check_doc_size.py --probe docs/PROGRESS.md=1000
                                                 # 阳性对照：临时压某文件预算，应 exit=1
                                                 # （门禁启用当天跑一次并留痕）
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============ 按你的项目改这里 ============
CONFIG = {
    # ① 字节预算：实测体积 × 1.5–2.5。值为 None 的项不查。
    "budgets": {
        "docs/PROGRESS.md": 300_000,
        "docs/DECISIONS.md": 200_000,
        # "docs/HANDOFF.md": 32_000,
    },
    # ② 单行字符上限（表格类文档可放宽）
    "line_limits": {
        "docs/PROGRESS.md": 4_000,
        "docs/DECISIONS.md": 12_000,
    },
    # ①② 超限时打印的处方（按文件；缺省用 DEFAULT 那条）
    "prescriptions": {
        "docs/PROGRESS.md": "按 PLAYBOOK §三：收官节/已关账行/旧更新移入 docs/archive/，原地留指针或区间行",
        "docs/DECISIONS.md": "按 PLAYBOOK §三：最老的 20–30 条移入对应百段档案，然后重跑 build_decisions_index.py",
        "DEFAULT": "按 PLAYBOOK §三 轮转对应历史进 docs/archive/",
    },
    # ③⑤ 决策账本；不用账本模式就整段设为 None
    "ledger": {
        "live": "docs/DECISIONS.md",
        "archive_glob": "docs/archive/DECISIONS-D*.md",
        "row_regex": r"^\| D(\d+) \| (\d{2}-\d{2}) \| (.*)\|\s*$",
        "index": "docs/DECISIONS-INDEX.md",
        "rebuild_cmd": "python3 tools/build_decisions_index.py",
    },
    # ④ 已关账任务行的归档文件；不用任务表模式就设为 None
    "tasks_archive": {
        "path": "docs/archive/PROGRESS-tasks-closed.md",
        "row_regex": r"^\|\s*\*{0,2}T\d+",
        "closed_word": "closed",                 # 每行必须含
        "status_col": 3, "runtime_col": 4,       # split("|") 后的列号
        "pending_word": "待验",                   # 状态列 closed 却仍含此词 → 自相矛盾
    },
}
# =========================================


# ---------- 纯判定（与 IO 分离，便于校准） ----------

def _size_verdict(nbytes, budget):
    return None if nbytes <= budget else (nbytes, budget)


def _line_verdict(lengths, limit):
    return [(i + 1, n) for i, n in enumerate(lengths) if n > limit]


def _contig_verdict(nums):
    if not nums:
        return "一条决策都没解析到"
    dup = sorted({n for n in nums if nums.count(n) > 1})
    if dup:
        return "编号重复：%s" % dup[:5]
    missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
    if missing:
        return "编号缺口：%s" % missing[:5]
    return None


def _hygiene_verdict(row, cfg):
    if cfg["closed_word"] not in row:
        return "未关账却进了归档"
    parts = row.split("|")
    if len(parts) > cfg["runtime_col"] and cfg["closed_word"] in parts[cfg["status_col"]] \
            and cfg["pending_word"] in parts[cfg["runtime_col"]]:
        return "状态列已关账但 runtime 列仍挂着「%s」" % cfg["pending_word"]
    return None


# ---------- 各检查 ----------

def _rx(rel, kind, problems, skipped):
    """配置了 → 返回绝对路径或记红；返回 None 表示本项不做。"""
    if rel is None:
        skipped.append(kind)
        return None
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        problems.append("%s %s 已配置但文件不存在——要么建它，要么从 CONFIG 移除（配置了就必须真在）" % (kind, rel))
        return None
    return p


def check_sizes(problems, notes, skipped, budgets):
    if not budgets:
        skipped.append("① 体积预算（未配置）")
        return
    rx = CONFIG["prescriptions"]
    for rel, budget in budgets.items():
        if budget is None:
            continue
        p = _rx(rel, "①", problems, skipped)
        if not p:
            continue
        n = os.path.getsize(p)
        if _size_verdict(n, budget):
            problems.append("① 体积超预算：%s 已 %s 字节 > 预算 %s —— %s"
                            % (rel, format(n, ","), format(budget, ","), rx.get(rel, rx["DEFAULT"])))
        else:
            notes.append("① %s ✅ %s / %s 字节（%d%%）" % (rel, format(n, ","), format(budget, ","), 100 * n // budget))


def check_line_lengths(problems, notes, skipped):
    limits = CONFIG.get("line_limits") or {}
    if not limits:
        skipped.append("② 单行长度（未配置）")
        return
    for rel, limit in limits.items():
        p = _rx(rel, "②", problems, skipped)
        if not p:
            continue
        lengths = [len(l) for l in open(p, encoding="utf-8").read().split("\n")]
        bad = _line_verdict(lengths, limit)
        if bad:
            where = "、".join("第 %d 行（%s 字符）" % (i, format(n, ",")) for i, n in bad[:3])
            problems.append("② 单行超限：%s %s > %s —— 这是「行内续写」单行怪物的形态，按 PLAYBOOK §三-1 整行替换＋归档"
                            % (rel, where, format(limit, ",")))
        else:
            notes.append("② %s ✅ 最长行 %s / %s 字符" % (rel, format(max(lengths), ","), format(limit, ",")))


def _collect_ledger(cfg):
    paths = sorted(glob.glob(os.path.join(ROOT, cfg["archive_glob"])))
    paths.append(os.path.join(ROOT, cfg["live"]))
    rows = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        for l in open(p, encoding="utf-8").read().split("\n"):
            m = re.match(cfg["row_regex"], l)
            if m:
                rows.setdefault(int(m.group(1)), []).append(l)
    return rows


def check_ledger_contiguity(problems, notes, skipped):
    cfg = CONFIG.get("ledger")
    if not cfg:
        skipped.append("③ 决策号完整性（未配置）")
        return
    if not _rx(cfg["live"], "③", problems, skipped):
        return
    rows = _collect_ledger(cfg)
    nums = [n for n, ls in rows.items() for _ in ls]
    v = _contig_verdict(nums)
    if v:
        problems.append("③ 决策号完整性：%s —— live＋归档合起来必须 1..max 每号恰一条（铁律「编号不动」）" % v)
    else:
        notes.append("③ 决策号 ✅ live＋归档共 %d 条，1..%d 连续无重" % (len(nums), max(nums)))


def check_archive_hygiene(problems, notes, skipped):
    cfg = CONFIG.get("tasks_archive")
    if not cfg:
        skipped.append("④ 归档任务行卫生（未配置）")
        return
    p = os.path.join(ROOT, cfg["path"])
    if not os.path.exists(p):
        skipped.append("④ 归档任务行（%s 尚不存在，项目还没归档过任务，正常）" % cfg["path"])
        return
    rows = [l for l in open(p, encoding="utf-8").read().split("\n") if re.match(cfg["row_regex"], l)]
    bad = [(l, _hygiene_verdict(l, cfg)) for l in rows]
    bad = [(l, w) for l, w in bad if w]
    if bad:
        head = "、".join("%s（%s）" % (l.split("|")[1].strip().strip("*")[:12], w) for l, w in bad[:3])
        problems.append("④ 归档任务行卫生：%d 行不合格 → %s —— 未关账的行不许归档" % (len(bad), head))
    else:
        notes.append("④ 归档任务行 ✅ %d 行全部关账且无自相矛盾" % len(rows))


def check_index_fresh(problems, notes, skipped):
    cfg = CONFIG.get("ledger")
    if not cfg or not cfg.get("index"):
        skipped.append("⑤ 索引新鲜度（未配置）")
        return
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_decisions_index
        want = build_decisions_index.build()
    except AssertionError as e:
        problems.append("⑤ 索引：重建失败（%s）——先修账本再谈索引" % e)
        return
    except ImportError:
        skipped.append("⑤ 索引（没装 build_decisions_index.py）")
        return
    p = os.path.join(ROOT, cfg["index"])
    have = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    if want != have:
        problems.append("⑤ 索引过期：%s 与账本重建结果不一致 —— 修法：`%s`" % (cfg["index"], cfg["rebuild_cmd"]))
    else:
        notes.append("⑤ 索引 ✅ 与账本确定性重建逐字一致")


# ---------- 自检 ----------

def _self_test():
    H = {"closed_word": "closed", "status_col": 3, "runtime_col": 4, "pending_word": "待验"}
    cases = [
        ("🔴 阳性：体积 1001 > 预算 1000 判红", _size_verdict(1001, 1000) is not None, True),
        ("阴性：体积恰等于预算 → 放行（预算含界）", _size_verdict(1000, 1000) is not None, False),
        ("🔴 阳性：一行 76234 字符 > 4000 判红", bool(_line_verdict([10, 76234], 4000)), True),
        ("阴性：最长行 3999 → 放行", bool(_line_verdict([3999], 4000)), False),
        ("🔴 阳性：决策号缺号判红", _contig_verdict([1, 2, 4]) is not None, True),
        ("🔴 阳性：决策号重复判红（live 与归档各留一份的形态）", _contig_verdict([1, 2, 2, 3]) is not None, True),
        ("阴性：1..4 连续 → 放行", _contig_verdict([1, 2, 3, 4]) is not None, False),
        ("🔴 阳性：归档行没关账判红", _hygiene_verdict("| **T9** | x | integrated | 待验 |", H) is not None, True),
        ("🔴 阳性：已关账＋待验自相矛盾判红", _hygiene_verdict("| **T9** | x | closed | 待验 |", H) is not None, True),
        ("阴性：已关账且 runtime 列 — → 放行", _hygiene_verdict("| **T9** | x | closed | — |", H) is not None, False),
    ]
    ok = True
    print("=== check_doc_size 自检（阳性+阴性校准）===")
    for desc, got, expect in cases:
        mark = "✅" if got == expect else "❌"
        ok = ok and got == expect
        print("  %s %s" % (mark, desc))
    print("\n%s" % ("✅ 全部符合预期（%d 例）" % len(cases) if ok else "❌ 有用例不符预期，本门禁不得启用"))
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return _self_test()

    budgets = dict(CONFIG.get("budgets") or {})
    for i, a in enumerate(sys.argv):
        if a == "--probe" and i + 1 < len(sys.argv):
            rel, _, val = sys.argv[i + 1].partition("=")
            budgets[rel] = int(val)
            print("⚠️ --probe：%s 预算临时压为 %s（阳性对照模式）" % (rel, val))

    problems, notes, skipped = [], [], []
    for fn in (lambda p, n, s: check_sizes(p, n, s, budgets), check_line_lengths,
               check_ledger_contiguity, check_archive_hygiene, check_index_fresh):
        try:
            fn(problems, notes, skipped)
        except Exception as e:  # 门禁自身不许卡住流程，但要说清哪项没跑成
            problems.append("%s 执行出错（本项未生效）：%r" % (getattr(fn, "__name__", "check"), e))

    print("=== 文档体积与归档体检 ===")
    for n in notes:
        print("  " + n)
    for s in skipped:
        print("  ⏭️ 跳过 " + s)
    if problems:
        print("\n❌ 发现 %d 处硬错：\n" % len(problems))
        for p in problems:
            print("  • " + p)
        print("\n处方在每条红后面；轮转规矩见 PLAYBOOK.md §三。不许调预算了事。")
        return 1
    if not notes:
        print("\n⚠️ 没有任何检查生效（全部未配置/跳过）——exit 0 不等于『已治理』，去改 CONFIG。")
        return 0
    print("\n✅ 生效的检查全部通过（%d 项生效，%d 项跳过）" % (len(notes), len(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
