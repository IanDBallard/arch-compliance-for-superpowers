class AcfError(Exception):
    """Base for all ACF failures (fail loud)."""


class RegistryLoadError(AcfError):
    pass


class UnknownMandateError(AcfError):
    pass


class UnknownDetectorError(AcfError):
    pass


class JudgeNotConfiguredError(AcfError):
    """LLM judge required (enforced detection:llm mandate) but no key/provider."""


class JudgeResponseError(AcfError):
    """The judge provider returned an unusable response (not a config issue)."""


class EmptyTargetTreeError(AcfError):
    pass


class DetectorPackError(AcfError):
    pass


class GitError(AcfError):
    """A git invocation required by ACF failed (bad ref, not a repo, etc.)."""


class BaselineError(AcfError):
    """Malformed, missing, or unwritable compliance baseline."""
