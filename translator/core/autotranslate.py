import logging
from argparse import Namespace
from pathlib import Path
from time import sleep
from typing import List, Tuple

from config_logging import config_logging
from structs.json import JSON
from structs.yaml import YAML
from translate_api import LibreTranslate
from translator.models.info_file import InfoFile

log = logging.getLogger(__name__)
config_logging(log, logging.INFO)


# config_logging(log, logging.DEBUG)

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

    def extract_parse_file(self, path=None, to_dict: bool = False) -> list[tuple[str, str]] or dict or None:
        # if not Path(path or self.path).exists():
        #     return {} if to_dict else []
        file_path = Path(path) if path else Path(self.path)
        if not file_path.exists():
            return {} if to_dict else []

        # if self.ext == 'json':
        #     json_instance = JSON(path or self.path)
        #     data = json_instance.get_content_json_file()
        #     if to_dict:
        #         return {k: v for k, v in json_instance.serializer_json(data)}
        #     return json_instance.serializer_json(data)
        # elif self.ext == 'yaml' or self.ext == 'yml':
        #     yml_instance = YAML(path or self.path)
        #     data = yml_instance.get_content_yaml_file()
        #     return yml_instance.serializer_yaml(data)
        # elif self.ext == 'ts':
        #     pass
        # else:
        #     raise ValueError(f"Formato no soportado {self.ext}")
        if self.ext.lower() == 'json':
            json_instance = JSON(str(file_path))
            data = json_instance.get_content_json_file()
            serialized = json_instance.serializer_json(data)
            return {k: v for k, v in serialized} if to_dict else serialized
        elif self.ext.lower() in ('yaml', 'yml'):
            yml_instance = YAML(str(file_path))
            data = yml_instance.get_content_yaml_file()
            return yml_instance.serializer_yaml(data)
        elif self.ext.lower() == 'ts':
            log.warning("Formato 'ts' aún no implementado.")
            return None
        else:
            raise ValueError(f"Formato no soportado {self.ext}")

    def json_worker(self, lang_work: list or str, lang_file: str, output_dir: str or Path, force: bool,
                    overwrite: bool):
        # base_data = self.extract_parse_file(to_dict=True)
        base_data = self.extract_parse_file(to_dict=True)
        if not isinstance(lang_work, list):
            lang_work = [lang_work]

        path_output = Path(output_dir) if output_dir else self.translations_dir
        path_output.mkdir(parents=True, exist_ok=True)

        # for l in lang_work:
        #     log.info(f'Traducir >> {l}')
        #     translated = []
        #
        #     path_output = Path(output_dir or self.translations_dir)
        #     path_output.mkdir(parents=True, exist_ok=True)
        #
        #     output_file = (path_output or self.translations_dir) / f"{l}.json"
        #     new_data = self.extract_parse_file(output_file, to_dict=True)
        #     # for i in range(len(base_data)):
        #     for i in base_data.keys():
        #         base_parse, base_value = i, base_data.get(i)
        #         out_paser, out_value = i, new_data.get(i)
        #         # print(f'base_parse: {base_parse} \nbase_value: {base_value} \nout_paser: {out_paser} '
        #         #       f'\nout_value: {out_value} \noverwrite {overwrite} \nforce {force}')
        #         if base_parse != out_paser or overwrite or force:
        #             log.debug(f'{base_parse} == {out_paser} and not {overwrite} or {force}')
        #             translate = self.api.translate(base_value, lang_file, l)
        #             log.info(f'{base_parse} ({lang_file}/{l}) => {translate}')
        #             translated.append((base_parse, translate))
        #         elif base_parse == out_paser and (not overwrite or not force) and out_value is not None:
        #             log.info(f'{base_parse} ({lang_file}/{l}) => {out_value}')
        #             translated.append((base_parse, out_value))
        #         elif base_parse == out_paser and (not overwrite or not force) and out_value is None:
        #             log.info(f'{base_parse} ({lang_file}/{l}) => {out_value}')
        #             translated.append((base_parse, out_value))
        #         # return
        #     json_instance = JSON(str(output_file))
        #     data = json_instance.deserializar_json(translated)
        #     json_instance.save_json_file(data)
        for lang in lang_work:
            log.info(f'Traduciendo al idioma: {lang}')
            translated: List[Tuple[str, str]] = []
            output_file = path_output / f"{lang}.json"

            # Se intenta leer el archivo traducido previamente, si existe
            try:
                new_data = self.extract_parse_file(output_file, to_dict=True)
            except Exception as e:
                log.info(f"No se pudo leer {output_file}, se creará uno nuevo. Error: {e}")
                new_data = {}

            for key, base_value in base_data.items():
                out_value = new_data.get(key)
                # Si no hay traducción previa o se indica forzar/overwrite, se traduce
                if out_value is None or overwrite or force:
                    log.debug(f"Traduciendo la clave: {key} (traducción previa: {out_value})")
                    try:
                        translated_text = self.api.translate(base_value, lang_file, lang)
                    except Exception as e:
                        log.error(f"Error al traducir {key}: {e}")
                        translated_text = None
                    log.info(f'{key} ({lang_file} -> {lang}): {translated_text}')
                    translated.append((key, translated_text))
                else:
                    log.info(f'Usando traducción existente para {key}: {out_value}')
                    translated.append((key, out_value))

            json_instance = JSON(str(output_file))
            try:
                # Se guarda el resultado en el archivo de salida
                json_instance.save_json_file(json_instance.deserializar_json(translated))
            except Exception as e:
                log.error(f"Error al guardar {output_file}: {e}")

            sleep(5)

    def worker(self, base: str = None, langs: list or str = None):
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
        # lang_file = base or self.args.base or self.name if self.name in self.language_support else self.lang_work
        # lang_work = (langs if langs in self.language_support else None) or self.args.langs or self.lang_work
        # if 'all' in lang_work:
        #     lang_work = [lang for lang in self.language_support if lang != lang_file]
        #
        # if self.ext == 'json':
        #     self.json_worker(lang_work, lang_file, self.args.output, self.force, self.overwrite)
        # else:
        #     log.error(f"Formato no soportado {self.ext}, notificar al administrador (waltercunbustamante@gmail.com)")
        if base:
            lang_file = base
        elif self.args and getattr(self.args, 'base', None):
            lang_file = self.args.base
        elif self.name in self.language_support:
            lang_file = self.name
        else:
            lang_file = self.lang_work

        # Determinar los idiomas de trabajo (lang_work)
        if langs:
            if isinstance(langs, list):
                lang_work = [lang for lang in langs if lang in self.language_support]
            elif isinstance(langs, str):
                lang_work = [langs] if langs in self.language_support else []
            else:
                lang_work = []
        elif self.args and getattr(self.args, 'langs', None):
            if isinstance(self.args.langs, list) and 'all' in self.args.langs:
                lang_work = [lang for lang in self.language_support if lang != lang_file]
            elif isinstance(self.args.langs, list):
                lang_work = [self.args.langs] if self.args.langs in self.language_support else []
            else:
                lang_work = []

        else:
            lang_work = [self.lang_work] if isinstance(self.lang_work, str) else self.lang_work

        # Si se especifica "all", se traducen todos menos el idioma base
        if 'all' in lang_work:
            lang_work = [lang for lang in self.language_support if lang != lang_file]

        if not lang_work:
            log.error("No se especificaron idiomas válidos para trabajar.")
            return None

        if self.ext.lower() == 'json':
            output_dir = self.args.output if self.args and getattr(self.args, 'output', None) else self.translations_dir
            self.json_worker(lang_work, lang_file, output_dir, self.force, self.overwrite)
        else:
            log.error(f"Formato no soportado {self.ext}. Notificar al administrador (waltercunbustamante@gmail.com)")
