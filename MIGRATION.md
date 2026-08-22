**English** ｜ [简体中文](MIGRATION.zh.md) ｜ [日本語](MIGRATION.ja.md)

# The Migration Manual: for projects that have already grown

New projects should just use `templates/` (see the README quick start). This manual is for projects whose **authoritative docs are already out of control**: how to move history into the archive without losing a single character. Source case: a private project seven weeks in — board 663 KB, ledger 819 KB, fattest single line 76,234 bytes; after migration the live files were 237 KB / 112 KB with zero history lost.

## Three iron rules (memorize before touching anything)

1. **Move, never edit**: pure relocation, not one character changed; proven by sha256 / multiset assertions (code below).
2. **Numbers never change**: decision and task IDs are permanent, so every "see D141"-style cross-reference in the repo still resolves after archiving.
3. **Script-verified conservation**: write to disk **only after every assertion passes** — if one fails, not a single byte is written. (Our own v1 script was stopped by its own assertions. It was right to be stopped.)

## The five-step order (between every step: all gates green → commit → push)

1. **Record the decision, then defuse the worst single-line monster.** Who approved, why, at what cost — into the ledger first; then move the mega-line wholesale into the archive (inserting newlines only, changing nothing), and replace it in the live file with a one-line snapshot plus the new "replace whole line" rule written right there.
2. **Move the board's three history blocks**: the stage log / closed task rows / the update log → three archive files, pointers left in place; use a **range row** in the task table (e.g. `| T1–T115 | … | closed | — |`) to keep "every task is addressable in the table" true.
3. **Archive the ledger in blocks of one hundred** (D001–D100 per file), keep the ~30 most recent live; generate the index.
4. **Bring the gate online** (`tools/check_doc_size.py`, edit CONFIG) + write the rules into your rules doc and "run the gate" into the agent entry doc. **The gate roster and the reading order must be updated in the same commit** — "a gate grew but the roster didn't" is a high-recurrence drift.
5. **Final sweep**: all gates green, `git status` clean, pushed; keep the migration scripts and their assertion output in the repo as evidence.

## Four field lessons (each one actually happened)

- **Anchor on content, not line numbers.** Locate sections by their headings (`find(lines, "## 2.")`), never by line number — with parallel sessions, someone else can shift your line numbers at any moment (the source project had another session land a commit mid-migration, same day).
- **Tools that read these docs must have their corpus extended in the same commit.** The source project had a "prior-art check" tool whose corpus was the task table; without folding the archive file into the corpus, the tool's own founding case would have become a false negative. Before moving anything, `grep -l` for every script that reads these docs.
- **State the unit before reporting a number.** BSD `awk length` counts bytes, Python `len` counts characters — more than a 2× difference on CJK text; the source project nearly shipped "76,234 characters" (actually bytes) into a doc, manufacturing fake drift for future auditors.
- **Run one real positive control after the move.** The day the gate goes live: `--probe` the budget below the current size → confirm red → restore → confirm green, and write those three steps into the work log — a measuring stick that is broken but still reports green is worse than no stick.

## Assertion snippets (copy into your migration script)

```python
from collections import Counter
import hashlib, re

# 1) Move-never-edit (whole-line relocations): original lines ==
#    new live lines ⊎ each batch of moved-out lines − explicitly
#    registered additions
new_c = Counter(new_lines) + Counter(moved_a) + Counter(moved_b)
new_c.subtract(added_to_live)          # pointers/range rows/stubs, registered one by one
diff  = {k: v for k, v in (new_c - Counter(orig_lines)).items() if k.strip()}
diff2 = {k: v for k, v in (Counter(orig_lines) - new_c).items() if k.strip()}
assert not diff and not diff2, ("extra", list(diff)[:3], "lost", list(diff2)[:3])

# 2) Move-never-edit (line-splitting): stripping the inserted newlines
#    must reproduce the original line exactly
assert split_text.replace("\n", "") == original_line
assert hashlib.sha256(split_text.replace("\n", "").encode()).hexdigest() == orig_sha

# 3) ID conservation: live + archives together must be 1..max,
#    exactly one row per ID
nums = sorted(all_ids)
assert nums == list(range(1, max(nums) + 1)), "gap or duplicate in IDs"

# 4) Task-row conservation + addressability (range rows expanded via
#    T(\d+)[–-]T?(\d+) must cover 1..N)
assert len(orig_rows) == len(archived_rows) + len(kept_rows)
```

## The shape of a migration script (reference)

The source project's two one-shot scripts (~150 lines each) follow this skeleton: idempotency assertion (refuse to run if the migration already happened) → content-anchored section extraction → assemble the new live file and archive bodies → **all assertions** → write archives and verify by reading back → write the live file → print the conservation numbers (chunk/line/byte counts go into the commit message). Assemble it from the snippets above.
