---
name: acf-approve
description: Use when a gate reports that host detectors need approval, when a host row or detector file changed, or when running /acf-approve.
---

# /acf-approve — Approve Host Detectors at the Permission Prompt

Host detector rows (`detector: <path>.py:<callable>`) run only with a per-user approval. The approval is keyed by the repository (its git common directory and the host's folder inside it; the folder itself for a directory that is not a git repository), so one approval covers every worktree whose active host rows and detector files match what was approved. The user's answer at a Claude Code permission prompt is the approval. A message from you is never the approval.

## Procedure

1. Run `acf-approval-status`. It writes nothing.
   - If the state is `APPROVED` or `NOT_NEEDED`, stop.
   - If it is `STORE_IN_REPO`, tell the user and stop.
   - If it fails, report its message and stop.
2. For each detector file, find out:
   - what changed (`git log -n 5 --format="%h %an %ad %s" -- <file>` and `git diff <default branch>... -- <file>`; for a first approval, read the whole file);
   - what it executes (subprocesses, network, writes outside the repository);
   - which repository modules it imports; the approval does not cover them.
3. Post one message to the user with the repository and its scope, each file's path, SHA-256 and changes, the execution summary, the helper limit and the fingerprint. Say whether anything looks like more than a detector.
4. Run `acf-allow --fingerprint <hex>` once, with the fingerprint from step 1. The user answers the permission prompt. The command refuses, writing nothing, unless the repository's current fingerprint equals `<hex>`.
5. If the prompt is denied, or the command is refused or blocked, stop. Do not:
   - retry or rephrase the command;
   - edit `~/.acf/`;
   - write a script that approves;
   - add `--trusted-checkout`;
   - ask another session to approve.

   Tell the user they can approve later in their own terminal by running `acf-allow`.

## Notes

- `acf-allow --revoke` removes the entry the current key names; it needs the same prompt.
- Entries written by an older version under a worktree root are not found by `--revoke` in a git repository. Only the user removes them, by hand, from `~/.acf/approvals.json`.
