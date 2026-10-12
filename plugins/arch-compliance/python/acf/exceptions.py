class AcfError(Exception):
    """Base for all ACF failures (fail loud)."""


class AcfInputError(AcfError):
    """An input file ACF must read is missing, unparsable, or misshapen."""


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


class TemplateRenderError(AcfError):
    """A template token had no value, or a supplied value had no token."""


class ReviewerContractViolationError(AcfError):
    """A reviewer payload does not satisfy the contract it was dispatched under."""


class SpecKindUndeterminedError(AcfError):
    """A spec is neither a defect nor a feature and is not declared docs/measurement."""


class CitationHistoryUnavailableError(AcfError):
    """A citation's history could not be read, so its kind cannot be decided."""


class LedgerWriteError(AcfError):
    """The efficacy ledger could not be appended to."""


class RunDetailWriteError(AcfError):
    """A run detail could not be written, so the run has no record."""


class UnresolvableCitationError(AcfError):
    """A spec cites a path that is not current, historical, proposed, asserted absent or external."""
