"""Registry-driven enforcement: the mandate registry, not the detectors,
decides what gates, at what severity, and what is exempt."""

from __future__ import annotations

from acf.enforcement import apply_registry
from acf.finding import Finding, Severity
from acf.registry import Mandate, MandateRegistry


def _mandate(
    mandate_id: str,
    *,
    severity: str = "BLOCK",
    status: str = "enforced",
    detector: str = "empty_catch",
    exemption_tokens: list[str] | None = None,
) -> Mandate:
    return Mandate(
        id=mandate_id,
        title="t",
        severity=severity,  # type: ignore[arg-type]
        detection="ast",
        detector=detector,
        languages="both",
        call_sites=["ci"],
        exemption_tokens=exemption_tokens if exemption_tokens is not None else [f"{mandate_id}-ok"],
        status=status,  # type: ignore[arg-type]
        arch_anchor="# x",
    )


def _registry(*mandates: Mandate) -> MandateRegistry:
    return MandateRegistry(mandates=list(mandates), source_path="test")


def _finding(mandate_id: str, *, severity: Severity = Severity.BLOCK, line: int = 1) -> Finding:
    return Finding(
        mandate_id=mandate_id,
        severity=severity,
        path="src/a.tsx",
        line=line,
        message="m",
        detector="d",
    )


def _no_lines(_path: str, _line: int) -> str:
    return ""


def test_finding_without_registry_row_is_dropped() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch"))
    out = apply_registry([_finding("no-shims.explicit-any")], reg, _no_lines)
    assert out == []


def test_unenforced_mandate_is_dropped() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch", status="unenforced"))
    out = apply_registry([_finding("fail-loud.empty-catch")], reg, _no_lines)
    assert out == []


def test_partial_mandate_is_kept() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch", status="partial"))
    out = apply_registry([_finding("fail-loud.empty-catch")], reg, _no_lines)
    assert len(out) == 1


def test_registry_severity_overrides_detector_severity() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch", severity="WARN"))
    out = apply_registry(
        [_finding("fail-loud.empty-catch", severity=Severity.BLOCK)], reg, _no_lines
    )
    assert out[0].severity == Severity.WARN


def test_double_slash_comment_exemption_for_typescript() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch"))

    def lines(_path: str, _line: int) -> str:
        return "  } catch {} // fail-loud.empty-catch-ok: legacy shim, tracked in #42"

    out = apply_registry([_finding("fail-loud.empty-catch")], reg, lines)
    assert out == []


def test_hash_comment_exemption_for_python() -> None:
    reg = _registry(_mandate("fail-loud.bare-except"))

    def lines(_path: str, _line: int) -> str:
        return "except Exception:  # fail-loud.bare-except-ok: top-level CLI guard"

    out = apply_registry([_finding("fail-loud.bare-except")], reg, lines)
    assert out == []


def test_exemption_without_reason_does_not_exempt() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch"))

    def lines(_path: str, _line: int) -> str:
        return "  } catch {} // fail-loud.empty-catch-ok:"

    out = apply_registry([_finding("fail-loud.empty-catch")], reg, lines)
    assert len(out) == 1


def test_enforced_block_survives_untouched() -> None:
    reg = _registry(_mandate("fail-loud.empty-catch"))
    out = apply_registry([_finding("fail-loud.empty-catch")], reg, _no_lines)
    assert len(out) == 1
    assert out[0].severity == Severity.BLOCK


def test_custom_exemption_token_from_registry_only() -> None:
    """Host can rename exemption_tokens; detectors must not hardcode the old form."""
    reg = _registry(
        _mandate("fail-loud.bare-except", exemption_tokens=["legacy-guard"])
    )
    raw = _finding("fail-loud.bare-except")

    def lines_old_form(_path: str, _line: int) -> str:
        return "except Exception:  # fail-loud.bare-except-ok: no longer in registry"

    assert apply_registry([raw], reg, lines_old_form)  # still gates

    def lines_custom(_path: str, _line: int) -> str:
        return "except Exception:  # legacy-guard: tracked in ticket 9"

    assert apply_registry([raw], reg, lines_custom) == []
