#!/usr/bin/env python3

import argparse
import json
import pathlib
import unicodedata
from collections.abc import Iterable
from types import TracebackType


class LanguageDataError(Exception):
    pass


class LanguageDataIndexPayload:
    """A class that helps manage word list files. It is constructed indirectly via the LanguageDataIndex class."""
    root_path: pathlib.Path
    path_mapping: dict[str, str]

    def __init__(self, root_path: pathlib.Path, path_mapping: dict[str, str]) -> None:
        self.root_path = root_path
        self.path_mapping = path_mapping

    def get_lang_codes(self) -> list[str]:
        return list(self.path_mapping.keys())

    def get_path(self, lang: str) -> pathlib.Path:
        if lang not in self.path_mapping:
            raise LanguageDataError(f'Unrecognized language {lang!r}')

        return self.root_path / f'{self.path_mapping[lang]}.txt'

    def read_language_file(self, lang: str) -> list[str]:
        try:
            with open(self.get_path(lang)) as file:
                return list(file.readlines())

        except OSError as err:
            raise LanguageDataError(f'Could not read language file {self.path_mapping[lang]}') from err

    def write_to_language_file(self, lang: str, words: list[str]) -> None:
        try:
            with open(self.get_path(lang), 'w') as file:
                file.writelines(words)

        except OSError as err:
            raise LanguageDataError(f'Could not open language file {self.path_mapping[lang]} for writing') from err


class LanguageDataIndex:
    """A context manager class that helps manage word list files. Sample usage:q

    with LanguageDataIndex() as lang_index:
        words = lang_index.read_language_file('en')
        ...
        lang_index.write_to_language_file('en', new_words)
    """
    root_path: pathlib.Path

    def __init__(self, root_path: pathlib.Path | None = None) -> None:
        if root_path is None:
            self.root_path = pathlib.Path(__file__).parent
        else:
            self.root_path = root_path

    def __enter__(self) -> LanguageDataIndexPayload:
        index_path = self.root_path / 'languages.json'

        try:
            with open(self.root_path / 'languages.json') as file:
                path_mapping = json.load(file)

        except OSError as err:
            raise LanguageDataError(f'Could not read language index file {index_path}') from err

        except json.JSONDecodeError as err:
            raise LanguageDataError(f'Could not parse the language index file {index_path}') from err

        if not isinstance(path_mapping, dict):
            raise LanguageDataError(f'Expected the language index file {index_path} to be a JSON dictionary')

        for key, value in path_mapping.items():
            if not isinstance(value, str) or not (self.root_path / f'{value}.txt').exists():
                raise LanguageDataError(f'Expected the key {key!r} in {index_path} to point to a valid language file')

        return LanguageDataIndexPayload(self.root_path, path_mapping)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None
     ) -> None:
        pass


def sort_word_list(lang: str, words: Iterable[str]) -> list[str]:
    """Sort a list of words using LibICU collation."""

    try:
        import icu
    except ImportError as err:
        raise LanguageDataError('PyICU is needed for proper unicode sorting') from err

    icu_locales = icu.Locale.getAvailableLocales()

    try:
        locale = icu_locales[lang]
    except KeyError as err:
        raise LanguageDataError(f'No ICU locale available for language {lang!r}') from err

    collator = icu.Collator.createInstance(locale)
    # Without maximizing the strength, that the Persian strings 'هیچ‌جور' (with a non-joiner) 'هیچجور' (without it) are reported as equal.
    collator.setStrength(icu.Collator.IDENTICAL)
    return sorted(words, key=collator.getSortKey)


def merge_language_files(lang_index: LanguageDataIndexPayload, lang: str, new_paths: list[str]) -> None:
    word_bag = {unicodedata.normalize('NFC', word) for word in lang_index.read_language_file(lang)}

    for path in new_paths:
        try:
            with open(path) as file:
                for word in file.readlines():
                    word_bag.add(unicodedata.normalize('NFC', word))

        except OSError as err:
            raise SystemExit(f'Could not read {path}. Aborting.') from err

    words = sort_word_list(lang, word_bag)
    lang_index.write_to_language_file(lang, words)


def cli() -> None:
    parser = argparse.ArgumentParser(prog='manage.py')
    subparsers = parser.add_subparsers(dest='command')

    parser_sort = subparsers.add_parser('sort', help='Sort an existing language file')
    parser_sort.add_argument('lang', help='Language code for file to sort. The code is also used for determining the locale.')

    subparsers.add_parser('sort-all', help='Sort all existing language files')

    parser_merge = subparsers.add_parser('merge', help='Merge new words into an existing language file')
    parser_merge.add_argument('lang', help='Language code for file to merge into. The code is also used for determining the locale.')
    parser_merge.add_argument('rest', nargs='*', help='Other files to merge.')

    result = parser.parse_args()

    match result.command:
        case 'sort':
            with LanguageDataIndex() as lang_index:
                merge_language_files(lang_index, result.lang, [])

        case 'sort-all':
            with LanguageDataIndex() as lang_index:
                for code in lang_index.get_lang_codes():
                    merge_language_files(lang_index, code, [])

        case 'merge':
            with LanguageDataIndex() as lang_index:
                merge_language_files(lang_index, result.lang, result.rest)

        case _:
            parser.print_usage()


if __name__ == '__main__':
    cli()
