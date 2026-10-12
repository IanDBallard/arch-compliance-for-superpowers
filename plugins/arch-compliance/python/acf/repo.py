"""Host repository layout: the one declaration of where ACF looks in a host.

Stdlib-only on purpose. Both hooks import this at module scope, before the
``.acf/enabled`` gate decides whether ACF is active at all, so this module must
never pull in a third-party package.
"""
from __future__ import annotations

from pathlib import Path

#: Host-relative directory holding the mandate registry and the doctrine document.
CONFIG_DIR = Path("config") / "architecture"

#: Host-relative path to the mandate registry.
MANDATES_REL = CONFIG_DIR / "mandates.yml"

#: Host-relative path to the host's architecture doctrine document.
ARCH_REL = CONFIG_DIR / "ARCHITECTURE.md"

#: Host-relative path to the adversarial-design-review gate's declaration.
ADR_REL = CONFIG_DIR / "adr.yml"

#: Host-relative default for the fail-loud ratchet baseline. A mandate may
#: override it via its ``params.baseline``; this is the value used when it does
#: not.
RATCHET_BASELINE_REL = CONFIG_DIR / "fail_loud_ratchet.json"

#: Host-relative marker that activates ACF in a host repository.
ENABLED_REL = Path(".acf") / "enabled"


def resolve_repo(explicit: Path | None, stdin_cwd: str | None = None) -> Path:
    """Resolve the host repository root.

    Precedence: an explicit ``--repo`` argument, then the invoking directory a
    harness supplies on stdin, then the process directory. The last branch is a
    genuine fallback, not a guarantee -- a caller that needs certainty must pass
    ``explicit``.
    """
    if explicit is not None:
        return explicit.resolve()
    if stdin_cwd:
        return Path(str(stdin_cwd)).resolve()
    return Path.cwd().resolve()
