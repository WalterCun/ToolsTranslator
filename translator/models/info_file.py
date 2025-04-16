# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
#
# """ translator/models/info_file.py """
#
# from dataclasses import dataclass
# from typing import Optional, Any, TypeVar, Type, cast
#
# __all__ = ["InfoFile"]
#
# T = TypeVar("T")
#
#
# def from_str(x: Any) -> str:
#     assert isinstance(x, str)
#     return x
#
# # noinspection Assert
# def from_none(x: Any) -> Any:
#     assert x is None
#     return x
#
#
# # noinspection TryExceptPass
# def from_union(fs, x):
#     for f in fs:
#         try:
#             return f(x)
#         except Exception:
#             pass
#     raise False
#
#
# # noinspection Assert
# def to_class(c: Type[T], x: Any) -> dict:
#     assert isinstance(x, c)
#     return cast(Any, x).to_dict()
#
#
# @dataclass
# class InfoFile:
#     #TODO mejorar el path y directorio para generar WindowsPath
#     path: Optional[str] = None
#     directory: Optional[str] = None
#     lang: Optional[str] = None
#     ext: Optional[str] = None
#     name: Optional[str] = None
#
#     @staticmethod
#     def from_dict(obj: Any) -> 'InfoFile':
#         assert isinstance(obj, dict)
#         path = from_union([from_str, from_none], str(obj.get("path")))
#         directory = from_union([from_str, from_none], str(obj.get("directory")))
#         lang = from_union([from_str, from_none], obj.get("lang"))
#         ext = from_union([from_str, from_none], obj.get("ext"))
#         name = from_union([from_str, from_none], obj.get("name"))
#         return InfoFile(path, directory, lang, ext, name)
#
#     def to_dict(self) -> dict:
#         result: dict = {}
#         if self.path is not None:
#             result["path"] = from_union([from_str, from_none], self.path)
#         if self.directory is not None:
#             result["directory"] = from_union([from_str, from_none], self.directory)
#         if self.lang is not None:
#             result["lang"] = from_union([from_str, from_none], self.lang)
#         if self.ext is not None:
#             result["ext"] = from_union([from_str, from_none], self.ext)
#         if self.name is not None:
#             result["name"] = from_union([from_str, from_none], self.name)
#         return result
