**English** ｜ [简体中文](README.zh.md) ｜ [日本語](README.ja.md)

# desk-and-drawer

**Keep your desk clear; put finished work in the drawer.** A governance kit that stops an AI-agent project's authoritative markdown docs (progress board, decision ledger) from growing without bound: a playbook + a size gate + starter templates + a migration manual.

## What this is

Long-running AI-collaboration projects (Claude Code / Codex / Cursor…) accumulate authoritative docs — a progress board, a decision ledger. **A doc with rules for writing but no rules for archiving grows without bound** — until any read or grep blows up the agent's context window, and every newly onboarded agent pays that tax again.

This repo is the cure, and everything stays in human-readable, git-native markdown:

- A methodology: [`PLAYBOOK.md`](PLAYBOOK.md) — the desk/drawer architecture and five rules bound to mandatory checkpoints
- Two scripts: [`tools/check_doc_size.py`](tools/check_doc_size.py) (the size gate — **a red is the single rotation trigger**) and [`tools/build_decisions_index.py`](tools/build_decisions_index.py) (a deterministic, mechanically generated ledger index)
- Four starter templates: [`templates/`](templates/) — decision ledger / progress board / agent entry doc / archive directory
- A migration manual: [`MIGRATION.md`](MIGRATION.md) — for projects that have already grown out of control, with copy-paste conservation assertions

## What this is not (related work)

An honest disclosure: **this is not an invention — it is a synthesis** of long-established practices (log rotation, ADRs, append-only ledgers, size caps). The gap it fills: nobody had packaged the *archive lifecycle* as an executable discipline.

| Project | What it does | Relation to this kit |
|---|---|---|
| [Beads](https://github.com/steveyegge/beads) | Replaces markdown task tracking with a git-embedded database | Different lane: it swaps the storage; this kit stays in markdown and governs the narrative docs. Complementary, not competing |
| [ctxlint](https://github.com/YawLabs/ctxlint) | Lints CLAUDE.md/AGENTS.md against your actual codebase | Adjacent: it fights drift in context files; this kit governs the lifecycle of authority docs |
| [agents-md](https://github.com/ivawzh/agents-md) | Composable AGENTS.md fragments with CI size limits | Adjacent: the same size-gate instinct, applied to agent instruction files |
| [AgentLinter](https://agentlinter.com/) | Scores and diagnoses CLAUDE.md | Adjacent: lints content quality; no history archiving |
| [memory-trail](https://github.com/frmoretto/memory-trail) | Decision memory + session logs | Adjacent: records the "why"; no rotation mechanism |
| ADR (Architecture Decision Records) | One decision per file + an index | One of the ideas this kit's ledger pattern descends from |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | Spec-driven development: Propose → Apply → **Archive** | Its Archive step shares this kit's "done means archived" principle |

Upstream ideas: Anthropic's [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); OpenAI Codex's hard 32 KiB cap on project docs (enforcement by tooling rather than willpower — the attitude this kit's gate inherits).

## Quick start (day one of a new project)

1. Copy `templates/docs/` into your repo — decision ledger / progress board / **agent entry doc `HANDOFF.md`** / archive directory, all in place.
2. Copy `tools/` over, edit the `CONFIG` block at the top of `check_doc_size.py` (file names + budgets; budget = measured size × 1.5–2.5), then run `python3 tools/build_decisions_index.py` once.
3. Open `docs/HANDOFF.md` and fill in the blanks; if your agent uses CLAUDE.md / AGENTS.md, paste its "fixed reading order + mandatory gates" section there.
4. Follow the rules from decision #1: one line per decision, contiguous numbering, append-only.
5. When the gate goes red, rotate as the red text prescribes — **never "fix" it by raising the budget**.

Already-grown project → go straight to [`MIGRATION.md`](MIGRATION.md).

## Wiring it into daily work (discipline must ride on mandatory actions)

- **Agent side**: the entry-doc template ships with the gate on its mandatory checklist — every new session runs it as takeover step one.
- **Human side**: to enforce at commit time, add a pre-commit hook:

  ```bash
  printf '#!/bin/sh\npython3 tools/check_doc_size.py || exit 1\n' > .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
  ```

- **CI side**: the script is stdlib-only with exit codes 0/1 — one line, `python3 tools/check_doc_size.py`, makes it a required check in any CI.

## Numbers from the field (a private iOS project, 7 weeks in)

Before: progress board 663 KB / 1,763 lines; decision ledger 819 KB with 274 decisions crammed into one table; **the fattest single line was 76,234 bytes** — any read or grep touching it blew up the agent's context window. After: live board 237 KB / 569 lines; ledger 112 KB (30 most recent decisions); longest line 1,688 chars; **zero history lost** (asserted by the migration scripts: stripped-newline reassembly matches the original by sha256; decision numbers 1..274 contiguous with no gaps or dupes; task rows 118 = 109 archived + 9 kept). Six commits, every gate green between each step.

## FAQ

**Q: Why not just use Beads?** For a brand-new project — absolutely consider it (PLAYBOOK §4). Pick this kit when the product owner needs to **read the markdown directly**, you don't want a binary dependency, or the project already has too many markdown assets to switch storage mid-flight.

**Q: After forking this into a project, which side wins?** The project's own rules doc. This repo is the upstream template; divergence after forking is normal evolution and doesn't need to flow back.

## License

MIT © 2026 TunaSaiko
