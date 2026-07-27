class AcfError(Exception):
    """Base for all ACF failures (fail loud)."""


class RegistryLoadError(AcfError):
    pass


class UnknownMandateError(AcfError):
    pass


class UnknownDetectorError(AcfError):
    pass


class JudgeNotConfiguredError(AcfError):
    pass


class EmptyTargetTreeError(AcfError):
    pass


class DetectorPackError(AcfError):
    pass


class BaselineError(AcfError):
    """Malformed, missing, or unwritable compliance baseline."""
