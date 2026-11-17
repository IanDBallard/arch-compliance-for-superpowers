# Architecture review

- Commit: e38bd7e064ceb31a02d44f59acae0ad7465f4645
- Invocation: /architecture-review --update-baseline

## Groups

| Group | Status | Findings |
| --- | --- | --- |
| fail-loud | OK | 6 |

## Findings

### important

- `plugins/arch-compliance/python/acf/judge.py:322` — fail-loud: silent success default on a failure path — soft.fail-loud
  - Why: A judge response that parses as a JSON object but lacks the `violation` key is read as 'no violation', so a malformed reply produces a clean result instead of a JudgeResponseError.
  - Snippet: `if not data.get("violation", False):
        return None`
  - Suggested fix: Require `violation` to be present and a bool, and raise JudgeResponseError when it is absent or the wrong type. Treat only an explicit false as no finding.

### nit

- `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:75` — fail-loud: interface probing — soft.fail-loud
  - Why: getattr with a default of 0 probes an AST node for an attribute that every ast.Call has, and 0 is below the minimum valid line of 1 on a Finding, so a missing attribute would be masked instead of raising.
  - Snippet: `line = getattr(node, "lineno", 0)`
  - Suggested fix: Read `node.lineno` directly. The same getattr pattern appears in fsm_guard.py:62 and python_pack.py:139 and :167.

### suggestion

- `plugins/arch-compliance/hooks/posttooluse_gate.py:219` — fail-loud: silent null on a load path — soft.fail-loud
  - Why: Malformed hook stdin JSON is swallowed and treated as no payload, so the gate falls back to text format and an empty path list; it may be a deliberate allowance for non-hook invocations, which needs human judgment.
  - Snippet: `except json.JSONDecodeError:
        return None`
  - Suggested fix: When stdin is non-empty and not valid JSON, report it and fail with the hook failure code, or document that absence of a parseable payload is a valid answer.
- `plugins/arch-compliance/hooks/inject_constraints.py:148` — fail-loud: silent null on a load path — soft.fail-loud
  - Why: Malformed hook stdin JSON is silently dropped and the hook proceeds as if no payload was sent; it may be an intended allowance for non-hook invocations, which needs human judgment.
  - Snippet: `except json.JSONDecodeError:
        return None`
  - Suggested fix: Report malformed non-empty stdin and exit non-zero, or document that an unparseable payload is a valid absent-payload case.
- `plugins/arch-compliance/python/acf/engine.py:66` — fail-loud: silent null on a parse path — soft.fail-loud
  - Why: A Python file that does not parse yields None, and python_pack.py:35-36 turns that into an empty finding list, so a syntactically broken changed file passes the scanners as clean; this is a documented skip convention, but the effect is a silent clean result.
  - Snippet: `except SyntaxError:
        return None`
  - Suggested fix: Surface unparsable changed files, for example as a warning finding or a reported skip, instead of returning no findings.
- `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/params_census.py:71` — fail-loud: swallowed failure — soft.fail-loud
  - Why: A tracked YAML file that fails to parse is silently skipped, so the census can report 'NOT-JSON: 0' without having examined every file; this is an evidence script, so severity needs human judgment.
  - Snippet: `except yaml.YAMLError:
            continue`
  - Suggested fix: Record the unparsable file as an explicit row, for example UNPARSABLE, so it appears in the printed census.

0 findings exempted by inline tokens.

## Roll-up

- Groups: OK: 1, FAILED: 0
- Findings by severity: blocking: 0, important: 1, nit: 1, suggestion: 4

no baseline (run --update-baseline to set one)

