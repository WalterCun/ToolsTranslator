"""Custom exceptions for ToolsTranslator."""

class ToolsTranslatorError(Exception):
    """Base exception for the package."""


class ServiceUnavailableError(ToolsTranslatorError):
    """Raised when LibreTranslate service is not available."""


class ExtraNotInstalledError(ToolsTranslatorError):
    """Raised when an optional feature is used without required extra."""


class TranslationFileError(ToolsTranslatorError):
    """Raised for translation file handling issues."""
