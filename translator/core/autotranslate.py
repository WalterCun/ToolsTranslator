import logging
from argparse import Namespace
from pathlib import Path

from yaml import serialize

from config_logging import config_logging
from structs.json import JSON
from structs.yaml import YAML
from translate_api import LibreTranslate
from translator.models.info_file import InfoFile

log = logging.getLogger(__name__)
config_logging(log, logging.INFO)


class AutoTranslate:
    """
    Class responsible for automating translation operations using the LibreTranslate
    API. It organizes file paths, manages input parameters, and ensures translation
    processes align with the provided metadata. This class also facilitates clean
    handling of directory structures and translation configurations.

    :ivar api: Instance of the LibreTranslate API handler for handling translation
        requests and results.
    :ivar path: File path for the target file to be translated.
    :type path: str
    :ivar translations_dir: Directory where translation results will be stored. If
        not present, it will be created.
    :type translations_dir: Path
    :ivar lang_work: Language to work on during translation. Defaults to 'all' if
        no language is specified.
    :type lang_work: str
    :ivar name: Name of the file to be translated.
    :type name: str
    :ivar ext: Extension of the file to be translated.
    :type ext: str
    :ivar force: Indicates whether to forcibly overwrite certain conditions during
        translation operations.
    :type force: bool
    :ivar overwrite: Indicates whether existing data should be overwritten during
        the translation process.
    :type overwrite: bool
    """

    def __init__(self, meta: InfoFile, force=False, overwrite=False, args: Namespace = None):
        """
        Initializes an instance of this class, responsible for setting up API usage,
        file paths, translation directories, and managing input parameters. This class
        is tailored to handle translation operations using the LibreTranslate API, and
        it organizes the environment based on the metadata provided.

        :param meta: Metadata for the translation. Contains relevant information about
            the file, its path, directory structure, and language details.
        :type meta: InfoFile
        :param force: Flag that indicates whether the operation should forcibly
            overwrite certain conditions during processing. Defaults to False.
        :type force: bool
        :param overwrite: Flag that indicates if existing data should be overwritten.
            Defaults to False.
        :type overwrite: bool
        """
        self.api = LibreTranslate()
        self.language_support = self.api.get_supported_languages(args.base or meta.lang or 'all', True)
        self.path = meta.path
        self.translations_dir = Path(meta.directory)
        if self.translations_dir.exists():
            self.translations_dir.mkdir(parents=True, exist_ok=True)
        self.lang_work = meta.lang or 'all'
        self.name = meta.name
        self.ext = meta.ext

        self.args = args

        self.force = force
        self.overwrite = overwrite

    def extract_parse_file(self, path=None) -> list[tuple[str, str]] or None:
        if not Path(path or self.path).exists():
            return None
        if self.ext == 'json':
            json_instance = JSON(path or self.path)
            data = json_instance.get_content_json_file()
            return json_instance.serializer_json(data)
        elif self.ext == 'yaml' or self.ext == 'yml':
            yml_instance = YAML(path or self.path)
            data = yml_instance.get_content_yaml_file()
            return yml_instance.serializer_yaml(data)
        elif self.ext == 'ts':
            pass
        else:
            raise ValueError(f"Formato no soportado {self.ext}")

    def json_worker(self, lang_work: list or str, lang_file: str, force: bool, overwrite: bool):
        base_data = self.extract_parse_file()

        translated = []

        for l in lang_work:
            log.info(f'Traducir >> {l}')
            output_file = self.translations_dir / f"{l}.json"
            new_data = self.extract_parse_file(output_file)
            print(new_data)
            for i in range(len(base_data)):
                base_parse, base_value = base_data[i]
                if not new_data:
                    out_paser, out_value = None, None
                else:
                    out_paser, out_value = new_data[i]

                if base_parse == out_paser and (not overwrite or not force) and out_value is not None:
                    log.debug(f'{base_parse} == {out_paser} and not {overwrite} or {force} and {out_value} is not None')
                    log.info(f'{base_parse} ({lang_file}/{l}) => {out_value}')
                    translated.append((base_parse, out_value))
                elif base_parse != out_paser and (overwrite or force):
                    log.debug(f'{base_parse} == {out_paser} and not {overwrite} or {force}')
                    translate = self.api.translate(base_value, lang_file, l)
                    log.info(f'{base_parse} ({lang_file}/{l}) => {translate}')
                    translated.append((base_parse, translate))

            json_instance = JSON(output_file or self.path)
            data = json_instance.deserializar_json(translated)
            json_instance.save_json_file(data)

    def worker(self, base: str = None, langs: list or str = None, force: bool = False, overwrite: bool = False):
        """
        Executes work-related tasks based on the provided parameters. This method performs
        actions specified for the given input languages and modifies the behavior based
        on the provided arguments, ensuring proper handling of work cases with optional
        overwriting or forced conditions. Throws an assertion error if no language is
        specified.

        :param base: Base path or configuration to be used during operations. Defaults to None.
        :type base: str, optional
        :param langs: Specifies the languages as a list or string for which the operations
                      will apply. Must not be None or empty.
        :type langs: list or str, optional
        :param force: If True, forces the operations to proceed, potentially bypassing
                      standard constraints. Defaults to False.
        :type force: bool, optional
        :param overwrite: If True, allows overwriting of existing data or configurations
                          during the operation. Defaults to False.
        :type overwrite: bool, optional
        :return: The result of the worker operation or None if the process terminates early.
        :rtype: Any
        """
        lang_file = base or self.args.base or self.name if self.name in self.language_support else self.lang_work
        lang_work = (langs if langs in self.language_support else None) or self.args.langs or self.lang_work
        if 'all' in lang_work:
            lang_work = self.language_support

        if self.ext == 'json':
            self.json_worker(lang_work, lang_file, force, overwrite)
        else:
            log.error(f"Formato no soportado {self.ext}, notificar al administrador (waltercunbustamante@gmail.com)")