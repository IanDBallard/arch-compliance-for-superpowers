# Security policy

## Reporting a vulnerability

Please do not open a public issue for a security problem. Use GitHub's private
vulnerability reporting for this repository instead:

https://github.com/IanDBallard/arch-compliance-for-superpowers/security/advisories/new

Include the plugin version (`plugins/arch-compliance/.claude-plugin/plugin.json`),
the host setup that reproduces the problem, and what an attacker gains. Reports are
acknowledged within seven days.

## Scope

This plugin runs Python hooks and detectors inside a host repository and dispatches
reviewer subagents against spec documents. Reports about the hooks executing or
reading something outside the host's declared configuration, or about the gate
writing records outside the declared `runs_dir` and `ledger_path`, are in scope.

## Supported versions

Only the latest release on `main` receives fixes.
