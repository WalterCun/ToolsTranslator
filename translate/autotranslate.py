from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from translate.adapter import LibreTranslateAdapter, TranslationAdapter
from translate.exceptions import LanguageDetectionError, ServerDependencyMissingError
from translate.fileinfo import TranslateFile
from translate.io_handlers import flatten, read_mapping, unflatten, write_mapping


@dataclass(slots=True)
class AutoTranslateOptions:
    base: str | None = None
    langs: list[str] = field(default_factory=list)
    output: Path | None = None
    force: bool = False
    overwrite: bool = False
    nested: bool = True


@dataclass(slots=True)
class AutoTranslateResult:
    generated_files: list[Path]
    total_keys: int
    translated_keys: int
    failed_keys: int


class AutoTranslate:
    """Optional advanced translator for language file generation.

    This component is intentionally isolated from core static file workflows.
    It only uses remote translation when a translation adapter is provided or
    when `use_server=True` with default LibreTranslate adapter.
    """

    def __init__(
        self,
        translate_file: TranslateFile,
        args: AutoTranslateOptions,
        adapter: TranslationAdapter | None = None,
        use_server: bool = False,
    ) -> None:
        self.translate_file = translate_file
        self.args = args
        self.adapter = adapter
        self.use_server = use_server

    def _detect_source_lang(self) -> str:
        if self.args.base:
            return self.args.base
        detected = self.translate_file.detect_lang_from_name()
        if detected:
            return detected
        raise LanguageDetectionError(
            "Unable to detect base language from filename. Pass `base` explicitly."
        )

    def _resolve_adapter(self) -> TranslationAdapter:
        if self.adapter is not None:
            return self.adapter
        if not self.use_server:
            raise ServerDependencyMissingError(
                "AutoTranslate requires a translation adapter when server mode is disabled. "
                "Provide `adapter=...` or enable server mode with `use_server=True`."
            )
        return LibreTranslateAdapter()

    def worker(self) -> AutoTranslateResult:
        source_lang = self._detect_source_lang()
        if not self.args.langs:
            raise ValueError("No target languages provided in `langs`.")

        adapter = self._resolve_adapter()
        source_data = read_mapping(self.translate_file.path)
        flat_source = flatten(source_data)

        output_dir = self.args.output or self.translate_file.directory
        generated: list[Path] = []
        translated_keys = 0
        failed_keys = 0

        for target_lang in self.args.langs:
            target_file = output_dir / f"{target_lang}{self.translate_file.extension}"
            if target_file.exists() and not self.args.overwrite:
                if not self.args.force:
                    continue
                existing_data = read_mapping(target_file)
                flat_target = flatten(existing_data)
            else:
                flat_target = {}

            for key, value in flat_source.items():
                if key in flat_target and not self.args.force:
                    continue
                try:
                    flat_target[key] = adapter.translate(value, source=source_lang, target=target_lang)
                    translated_keys += 1
                except ServerDependencyMissingError:
                    failed_keys += 1
                    flat_target[key] = value

            to_write: dict[str, Any]
            if self.args.nested:
                to_write = unflatten(flat_target)
            else:
                to_write = flat_target

            write_mapping(target_file, to_write)
            generated.append(target_file)

        return AutoTranslateResult(
            generated_files=generated,
            total_keys=len(flat_source) * len(self.args.langs),
            translated_keys=translated_keys,
            failed_keys=failed_keys,
        )

    @classmethod
    def cli_worker(
        cls,
        translate_file: TranslateFile,
        args: AutoTranslateOptions,
        use_server: bool,
        adapter: TranslationAdapter | None = None,
    ) -> tuple[int, str]:
        """Helper for CLI integration with controlled messages and exit code."""
        try:
            result = cls(translate_file=translate_file, args=args, adapter=adapter, use_server=use_server).worker()
            generated = ", ".join(str(p) for p in result.generated_files) or "none"
            return (
                0,
                f"AutoTranslate completed. files=[{generated}] translated={result.translated_keys} failed={result.failed_keys}",
            )
        except ServerDependencyMissingError as exc:
            return (
                2,
                f"AutoTranslate requires server support. {exc}",
            )
        except Exception as exc:
            return (1, f"AutoTranslate failed: {exc}")
