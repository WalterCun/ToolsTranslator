"""Custom exceptions for ToolsTranslator."""


class ToolsTranslatorError(Exception):
    """Base exception for the package."""


class ServiceUnavailableError(ToolsTranslatorError):
    """Raised when LibreTranslate service is not available."""


class ExtraNotInstalledError(ToolsTranslatorError):
    """Raised when an optional feature is used without required extra."""


class TranslationFileError(ToolsTranslatorError):
    """Raised for translation file handling issues."""


class LanguageNotAvailableError(ToolsTranslatorError):
    """Raised when active language cannot be loaded and no fallback is available."""


# --------------------------------------------------------

class AutoTranslateError(Exception):
    """Base error for AutoTranslate workflows."""


class ServerDependencyMissingError(AutoTranslateError):
    """Raised when remote translation support is requested but unavailable."""


class LanguageDetectionError(AutoTranslateError):
    """Raised when source language cannot be auto-detected."""
