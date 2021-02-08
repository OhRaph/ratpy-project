"""Ratpy Pretty Printer """


# ############################################################### #
# ############################################################### #


def _colorize(text, lexer, *args, colorize=True, **kwargs):
    import sys
    if not colorize or not sys.stdout.isatty():
        return text
    try:
        from pygments import highlight
        from pygments.formatters import TerminalFormatter
        return highlight(text, lexer, TerminalFormatter())
    except ImportError:
        return text

# ############################################################### #
# ############################################################### #


def pformat_python(obj, *args, **kwargs):
    from pprint import pformat
    if isinstance(obj, str):
        text = obj
    else:
        text = pformat(obj, indent=4, width=160)
    try:
        from pygments.lexers import PythonLexer
        return _colorize(text, PythonLexer(), *args, **kwargs)
    except ImportError:
        return text


def pprint_python(obj, *args, **kwargs):
    print(pformat_python(obj, *args, **kwargs))


# ############################################################### #

def pformat_html(obj, *args, **kwargs):
    import bs4
    text = bs4.BeautifulSoup(obj, 'html.parser').prettify()
    try:
        from pygments.lexers import HtmlLexer
        return _colorize(text, HtmlLexer(), *args, **kwargs)
    except ImportError:
        return text


def pprint_html(obj, *args, **kwargs):
    print(pformat_html(obj, *args, **kwargs))

# ############################################################### #


def pformat_json(obj, *args, **kwargs):
    import json
    if isinstance(obj, str):
        obj = json.loads(obj)
    text = json.dumps(obj, indent=2, sort_keys=False, default=str)
    try:
        from pygments.lexers import JsonLexer
        return _colorize(text, JsonLexer(), *args, **kwargs)
    except ImportError:
        return text


def pprint_json(obj, *args, **kwargs):
    print(pformat_json(obj, *args, **kwargs))

# ############################################################### #
# ############################################################### #
