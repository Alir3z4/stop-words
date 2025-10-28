Stop Words
==========

List of common stop words in various languages.

The words are [normalized](http://www.unicode.org/faq/normalization.html) to Unicode's [normal form C](https://www.unicode.org/glossary/#normalization_form_c).

Maintaining the lists
---------------------

There is a `manage.py` script useful for maintaining the word lists.

To merge the English word list with new lists, you can use the following:
```python
python -m manage merge en /tmp/new_list.txt /tmp/another_new_list.txt
```

The language code above is used for two purposes:

  1. Determining the source file based on [`languages.json`](./languages.json)
  2. Determining the [libICU locale](https://unicode-org.github.io/icu/userguide/locale/#the-locale-concept) to use when comparing words

If new words are added manually, you can use the following to maintain the sorting order:
```python
python -m manage sort en
```

The management script contains code that can be used as a library. See the `LanguageDataIndex` class and the `sort_word_list` function for more details.

Available languages
-------------------
* Arabic
* Bulgarian
* Catalan
* Chinese
* Czech
* Danish
* Dutch
* English
* Finnish
* French
* German
* Greek
* Gujarati
* Hindi
* Hebrew
* Hungarian
* Indonesian
* Malaysian
* Italian
* Japanese
* Korean
* Norwegian
* Polish
* Portuguese
* Romanian
* Russian
* Slovak
* Spanish
* Swedish
* Turkish
* Ukrainian
* Vietnamese
* Persian/Farsi

Contributing
-----------------
You know how ;)


Programming languages support
-----------------------------

* `Python`: https://github.com/Alir3z4/python-stop-words
* `dotnet`: https://github.com/hklemp/dotnet-stop-words
* `rust`: https://github.com/cmccomb/rust-stop-words


License
--------
[Attribution 4.0 International (CC BY 4.0)][LICENSE]

[LICENSE]: http://creativecommons.org/licenses/by/4.0/
