"""Host detector loader and wrapped runners.

A host row's ``detector`` is ``<posix_rel_path.py>:<callable_name>``. The loader
imports the host module at dispatch and the runners call the callable inside one
wrapped region, so host code can neither crash nor corrupt the gate.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import sys
from collections.abc import Callable, Iterable, MutableMapping, Sequence
from pathlib import Path
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

from acf.engine import parse_python, validate_hit_fields, validate_posix_rel_path
from acf.exceptions import AcfInputError, DetectorPackError, UnknownDetectorError
from acf.finding import Finding, Severity
from acf.registry import Mandate, MandateRegistry, parse_host_detector_ref
from acf.repo import RepoTree

_ACTIVE_ROOT: Path | None = None


class HostHit(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: Annotated[str, AfterValidator(validate_posix_rel_path)]
    line: int
    message: str

    @model_validator(mode="before")
    @classmethod
    def _exact_fields(cls, data: object) -> object:
        if not isinstance(data, dict) or type(data.get("path")) is not str:
            raise ValueError("HostHit path must be exactly a str")
        validate_hit_fields(data.get("line"), data.get("message"))
        return data


def _describe(exc: BaseException) -> str:
    try:
        return f"{type(exc).__name__}: {exc}"
    except KeyboardInterrupt:
        raise
    except BaseException:  # fail-loud.bare-except-ok: a host exception whose __str__ or type name raises is still reported
        return "host exception (message unavailable)"


def load_host_detector(repo_root: Path, detector: str) -> Callable[..., Iterable[HostHit]]:
    global _ACTIVE_ROOT
    rel_path, attr = parse_host_detector_ref(detector)
    tree = RepoTree(repo_root)
    root = tree.root
    if _ACTIVE_ROOT is None:
        sys.path.append(str(root))
        _ACTIVE_ROOT = root
    elif root != _ACTIVE_ROOT:
        raise AcfInputError(
            f"host detectors already loaded from {_ACTIVE_ROOT.as_posix()}; one host root per process"
        )
    try:
        module_path = tree.file(rel_path)
    except OSError as exc:
        raise UnknownDetectorError(
            f"host detector {detector!r}: cannot stat {rel_path!r}: {_describe(exc)}"
        ) from exc
    if module_path is None:
        raise UnknownDetectorError(f"host detector {detector!r}: no file {rel_path!r} in the repository")
    name = "_acf_host_" + hashlib.sha256(rel_path.encode()).hexdigest()[:16]
    cached = sys.modules.get(name)
    mod = cached
    try:
        if mod is None:  # not loaded yet
            spec = importlib.util.spec_from_file_location(name, module_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"no loader for {rel_path!r}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        fn = getattr(mod, attr, None)
    except KeyboardInterrupt:
        raise
    except BaseException as exc:  # fail-loud.bare-except-ok: host module code may raise anything; it is re-raised as UnknownDetectorError
        if cached is None:  # this call registered it
            sys.modules.pop(name, None)
        raise UnknownDetectorError(
            f"failed to load host detector {detector!r} from {rel_path!r}: {_describe(exc)}"
        ) from exc
    if not callable(fn):
        raise UnknownDetectorError(f"host detector {detector!r}: {attr!r} is not a callable in {rel_path!r}")
    return fn


def _revalidate(item: object) -> HostHit:
    if type(item) is not HostHit:
        raise TypeError(f"yielded {type(item).__name__}, not HostHit")
    return HostHit.model_validate(dict(item.__dict__))


def _call_host(
    fn: Callable[..., Iterable[HostHit]], mandate: Mandate, where: str, *args: Any, **kwargs: Any
) -> list[HostHit]:
    try:
        raw = fn(*args, **kwargs)
        if raw is None or isinstance(raw, (str, bytes)):
            raise TypeError(f"returned {type(raw).__name__}, not an iterable of HostHit")
        items = list(raw)
        hits = [_revalidate(item) for item in items]
    except KeyboardInterrupt:
        raise
    except BaseException as exc:  # fail-loud.bare-except-ok: host detector code may raise anything; it is re-raised as DetectorPackError
        raise DetectorPackError(
            f"host detector {mandate.detector!r} for mandate {mandate.id!r} failed {where}: {_describe(exc)}"
        ) from exc
    return hits


def _to_findings(
    hits: list[HostHit], mandate: Mandate, *, repo_root: Path, expected_path: str | None
) -> list[Finding]:
    tree = RepoTree(repo_root)
    findings: list[Finding] = []
    for hit in hits:
        if tree.contained(hit.path) is None:
            raise DetectorPackError(
                f"host detector {mandate.detector!r} for mandate {mandate.id!r} "
                f"reported {hit.path!r}, which is outside the repository"
            )
        if expected_path is not None and hit.path != expected_path:
            raise DetectorPackError(
                f"host detector {mandate.detector!r} for mandate {mandate.id!r} "
                f"reported {hit.path!r}; an ast detector may report only {expected_path!r}"
            )
        findings.append(
            Finding(
                mandate_id=mandate.id,
                severity=Severity(mandate.severity),
                path=hit.path,
                line=hit.line,
                message=hit.message,
                detector=mandate.detector,
                detection=mandate.detection,
            )
        )
    return findings


def scan_host_ast_file(
    repo_root: Path,
    text: str,
    path: str,
    added_lines: frozenset[int] | None,
    registry: MandateRegistry,
    *,
    language: str,
    call_sites: frozenset[str],
) -> list[Finding]:
    mandates = [
        m
        for m in registry.host_rows(call_sites, detection="ast")
        if m.languages in {language, "both"}
    ]
    if not mandates:
        return []
    tree: ast.Module | None = None
    if language == "python":
        tree = parse_python(text)
        if tree is None:
            return []
    findings: list[Finding] = []
    for mandate in mandates:
        fn = load_host_detector(repo_root, mandate.detector)
        hits = _call_host(
            fn, mandate, f"on {path!r}", text, path, added_lines, tree=tree, params=mandate.params
        )
        findings.extend(_to_findings(hits, mandate, repo_root=repo_root, expected_path=path))
    return findings


def scan_host_guards(
    repo_root: Path,
    changed_files: Sequence[str],
    registry: MandateRegistry,
    file_lines: MutableMapping[str, list[str]],
    *,
    call_sites: frozenset[str],
) -> list[Finding]:
    mandates = registry.host_rows(call_sites, detection="guard")
    tree = RepoTree(repo_root)
    findings: list[Finding] = []
    for mandate in mandates:
        fn = load_host_detector(repo_root, mandate.detector)
        hits = _call_host(fn, mandate, "as a guard", tree.root, tuple(changed_files), params=mandate.params)
        found = _to_findings(hits, mandate, repo_root=repo_root, expected_path=None)
        for finding in found:
            if finding.path in file_lines:
                continue
            try:
                candidate = tree.file(finding.path)
                file_lines[finding.path] = (
                    []
                    if candidate is None
                    else candidate.read_text(encoding="utf-8", errors="replace").splitlines()
                )
            except OSError as exc:
                raise DetectorPackError(
                    f"host detector {mandate.detector!r} for mandate {mandate.id!r}: "
                    f"cannot read flagged file {finding.path!r}: {_describe(exc)}"
                ) from exc
        findings.extend(found)
    return findings
