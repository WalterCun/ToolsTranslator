from __future__ import annotations


class AutoTranslateError(Exception):
    """Base error for AutoTranslate workflows."""


class ServerDependencyMissingError(AutoTranslateError):
    """Raised when remote translation support is requested but unavailable."""


class LanguageDetectionError(AutoTranslateError):
    """Raised when source language cannot be auto-detected."""
