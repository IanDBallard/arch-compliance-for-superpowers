# CLAUDE.md — arch-compliance-for-superpowers

**Doctrine:** `config/architecture/ARCHITECTURE.md` and `config/architecture/mandates.yml`;
read both before substantive work. This repository is a host of its own
adversarial-design-review gate (`docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`).

## Superpowers skill defaults — repository overrides

When a skill's default and a rule below conflict, the rule below wins.

- **Spec location:** `docs/design/<TOPIC_IN_SCREAMING_SNAKE_CASE>.md`, not the
  `brainstorming` skill's `docs/superpowers/specs/` default.
- **Plan location:** `docs/plans/PLAN_<TOPIC_IN_SCREAMING_SNAKE_CASE>.md`, not the
  `writing-plans` skill's `docs/superpowers/plans/` default.
- **Brainstorming terminal state:** `/arch-compliance:adversarial-design-review <spec>`,
  then `writing-plans`. Only `CLEARED`, `CLEARED_WITH_ABSORPTIONS` (absorptions folded
  in) or `CLEARED_BY_VERIFICATION_PASS` proceeds to plan-writing. The last is a
  precision-only revision verified as the gate skill's verification pass states, with the
  user's approval minted in the spec header; a mechanism revision still needs a full run. `BLOCKED` returns to the spec through
  `arch-compliance:responding-to-adversarial-review`; the re-run scope follows the
  revision class as the gate skill states it.
- **Before any gate or post-merge-housekeeping run:** `python scripts/check_installed_skills.py <INSTALL_PATH>`
  (`INSTALL_PATH` is the plugin's `installPath` in
  `~/.claude/plugins/installed_plugins.json`). The rule and what to do on a mismatch are
  the doctrine's `## Release discipline`; never hand-run the review.

## Citation convention for specs here

Unprefixed paths are this repository. Another repository is cited with a prefix for the
reader (for example `hm:` for HistoricMansions) and its rule is quoted, never only
pointed to, so the spec is complete on its own. Before classifying citations, the gate's
controller maps each prefix to the sibling checkout and hands reviewers the mapped paths,
as spec §0 of `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` states.

## Windows note

Run the diff gate from the repository root with `PYTHONUTF8=1`
(`PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main`) until the git
runner declares its own encoding (spec §9, follow-up 1).
