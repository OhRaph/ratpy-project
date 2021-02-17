""" Ratpy Utils module """

import hashlib
import re
import sys
import unidecode

from importlib import import_module
from pkgutil import iter_modules

from ratpy.utils.checker.attributes import Attribute, AttributeParams, AttributesSet, AttributesChecker
from ratpy.utils.checker.functions import Function, FunctionParams, FunctionsSet, FunctionsChecker
from ratpy.utils.logger import Logger
from ratpy.utils.monitor import monitored

from ratpy.utils.path import *

__all__ = [
    'Utils', 'NotConfigured',
    'Logger', 'monitored',
    'Attribute', 'AttributeParams', 'AttributesSet', 'AttributesChecker',
    'Function', 'FunctionParams', 'FunctionsSet', 'FunctionsChecker',
    'sizeof', 'normalize', 'to_unicode', 'to_bytes', 'to_md5sum', 'load_object', 'create_instance'
    ]

# ############################################################### #
# ############################################################### #


class NotConfigured(Exception):
    pass

# ############################################################### #


class Utils(AttributesChecker, FunctionsChecker):

    """ Ratpy Utils class """

    def __init__(self, *args, **kwargs):
        AttributesChecker.__init__(self, *args, **kwargs)
        FunctionsChecker.__init__(self, *args, **kwargs)

    @property
    def infos(self):
        infos = super().infos
        infos['attributes'] = list(self.attributes)
        infos['functions'] = list(self.functions)
        return infos

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

# ############################################################### #
# ############################################################### #


def sizeof(obj, seen=None):
    size = 0
    if seen is None:
        seen = set()
    _id = id(obj)
    if _id not in seen:
        size = sys.getsizeof(obj)
        seen.add(_id)
        if isinstance(obj, dict):
            size += sum([sizeof(v, seen) for v in obj.values()])
            size += sum([sizeof(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += sizeof(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([sizeof(i, seen) for i in obj])
    return size

# ############################################################### #


def normalize(content, *args):

    res = content.lower()
    res = re.sub('[ ]+', '_', res)
    res = re.sub('[\\W]+', '_', res)
    res = re.sub('[_]+', '_', res)
    res = res.strip('_')
    res = unidecode.unidecode(res)
    # print('{} : {}'.format(res, content))
    return res

# ############################################################### #


def to_unicode(text, encoding=None, errors='strict'):
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError('to_unicode must receive a bytes or str object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)


def to_bytes(text, encoding=None, errors='strict'):
    if isinstance(text, bytes):
        return text
    if not isinstance(text, str):
        raise TypeError('to_bytes must receive a str or bytes object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.encode(encoding, errors)


def to_md5sum(file):
    m = hashlib.md5()
    while True:
        d = file.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

# ############################################################### #


def load_object(path):
    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


def walk_modules(path):
    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def create_instance(objcls, settings, crawler, *args, **kwargs):
    if settings is None:
        if crawler is None:
            raise ValueError("Specify at least one of settings and crawler.")
        settings = crawler.settings
    if crawler and hasattr(objcls, 'from_crawler'):
        instance = objcls.from_crawler(crawler, *args, **kwargs)
        method_name = 'from_crawler'
    elif hasattr(objcls, 'from_settings'):
        instance = objcls.from_settings(settings, *args, **kwargs)
        method_name = 'from_settings'
    else:
        instance = objcls(*args, **kwargs)
        method_name = '__new__'
    if instance is None:
        raise TypeError("%s.%s returned None" % (objcls.__qualname__, method_name))
    return instance

# ############################################################### #
# ############################################################### #


