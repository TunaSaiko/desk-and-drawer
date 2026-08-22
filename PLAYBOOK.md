**English** ｜ [简体中文](PLAYBOOK.zh.md) ｜ [日本語](PLAYBOOK.ja.md)

# The Playbook: Doc Size Governance for AI-Collaboration Projects

> Once forked into a real project, that project's own rules doc wins; this file is the upstream template.
> Section numbers are parallel across the three languages (§1 here = §一 in Chinese = §1 in Japanese).

## 1. The problem and its root cause

In a long-running AI-collaboration project, the authoritative docs — the progress board, the decision ledger — **grow without bound whenever they have rules for writing but no rules for archiving**. Nobody is being lazy; it is structural: append-only with no rotation has no upper bound by construction.

The typical endgame (real numbers in the README): a board of several hundred KB, and a single line that successive agents kept "appending in place" until it reached tens of thousands of bytes. The consequences come as a chain: reading the file floods the context window → information gets read incompletely → information gets read *wrongly*. **Every newly onboarded agent pays this tax again.**

## 2. Target architecture: desk vs drawer

| Layer | What lives there | Size policy |
|---|---|---|
| **Entry doc** (HANDOFF / CLAUDE.md style) | Only "how to take over"; zero dynamic state | Small and stable (cf. OpenAI Codex's hard 32 KiB cap) |
| **Current truth** (PROGRESS style) | The present stage / in-flight tasks / debts / backlog | Byte budget; rotate when exceeded |
| **Ledger, live segment** (DECISIONS style) | The ~30 most recent decisions | Byte budget |
| **Index** (derived) | One-line-per-entry, mechanically generated summary | Rebuildable at any time; **never authoritative** |
| **Archive** `docs/archive/` | All historical logs (append-only) | No limit — cold storage, grep on demand |

The reading discipline matches the architecture: **history is grepped on demand, never read cover to cover**; when an agent reads a large doc, it takes the heading outline first, then reads targeted sections.

## 3. Five rules, each bound to a mandatory action (never to "remembering")

1. **The status line is replaced whole; appending in place is forbidden.** The replaced old line is appended verbatim to the archive file on the spot. The single-line monster is exactly what the "append in place" habit manufactures.
2. **Done means archived**: when a stage closes, its whole section moves to the archive, leaving a one-line pointer in place; when a task closes, its table row moves to the archive and folds into a range row (e.g. `T1–T115`) — the range row keeps existing checks like "every task is addressable in the table" satisfied.
3. **The ledger archives in blocks of one hundred** (D001–D100 per file — the number alone tells you which file), and the live file keeps only the ~30 most recent entries, paired with a **mechanically generated, deterministic** index (deterministic = same input, same output, no timestamps — so "regenerate == file on disk" doubles as a freshness check).
4. **Size is guarded by a gate script, and a red is the single rotation trigger.** Discipline written into a log does nothing — it must ride on a script. Deliberately a *single* trigger: no second trigger like "N entries reached", so two rules can never fight. When the gate goes live, calibrate with **positives and negatives** (inject a real violation to prove it catches; prove normal flow doesn't false-alarm), and run one real positive control the day you enable it (temporarily push the budget below the current size → red → restore → green).
5. **Three iron rules for migration and rotation**:
   - **Move, never edit**: pure relocation, mechanically re-checkable (sha256 / multiset assertions — see the snippets in MIGRATION.md);
   - **Numbers never change**: decision and task IDs are permanent, so every cross-reference in the repo survives;
   - **Script-verified conservation**: after moving, mechanically verify every ID still exists and the total is unchanged — **if an assertion fails, nothing is written to disk**.
   And one umbrella principle: **archiving ≠ deleting**. Archives are append-only too; to supersede an archived conclusion, add a new entry in the live doc naming what it replaces — the original text stays untouched.

## 4. Day one on a new project

- Create `docs/` + `docs/archive/`; the entry doc pins a fixed reading order, and history always goes to the archive, grepped on demand.
- Start the decision ledger on day one with "one line per decision, contiguous numbering"; write down the append-only and supersession rules.
- Bring the gate script in within the first week (budgets can start loose and tighten later); budget = measured size × 1.5–2.5 headroom.
- You can also just start with an existing tool (zero migration cost on a fresh project is their best case): Beads (a git-embedded task database for agents), Backlog.md (one task, one markdown file), OpenSpec (the Propose → Apply → Archive lifecycle). **Mid-flight migration is another matter** — the project this playbook comes from evaluated the options and chose to keep its tools and just adopt the rules.

## 5. Migrating a project that has already grown

See `MIGRATION.md` (the five-step order plus assertion snippets). The three sentences that matter most, up front:

- Migration scripts **anchor on content, never on line numbers** — with multiple sessions working in parallel, someone else can shift your line numbers at any moment (the source project got hit by exactly this on migration day).
- **Any tool that reads these docs must have its corpus extended in the same commit** — the source project had a "prior-art check" tool whose corpus was the task table; had the archived rows not been folded in, the tool's own founding case would have become a false negative.
- Between every step: all gates green → commit → push.

## 6. Writing the red text

Every red must **carry its prescription inline** ("over budget → go do this specific action"), not just report "over". A gate that cries wolf is worse than no gate; likewise, **a measuring stick that can silently report green is worse than no stick** — every calibration includes one control of the form "test something that was never changed, and confirm the stick can actually measure it".

Two field lessons, now hard-coded into the tool comments:

- BSD `awk length` counts **bytes**; Python `len` counts **characters** — state the unit before you report a number;
- "All checks skipped" is not "passed": when nothing is configured and everything skips, say loudly that *no check took effect* — otherwise exit 0 gets read as "governed".
