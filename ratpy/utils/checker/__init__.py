""" Ratpy Checker module """

__all__ = [
    'CheckerException', 'CheckerItem', 'CheckerItemParams', 'CheckerItemsSet', 'Checker',
    'create_set'
]

from collections import namedtuple
from functools import reduce

from ratpy.utils.logger import Logger

# ############################################################### #
# ############################################################### #


def types_to_str(types):
    if isinstance(types, (tuple, list)):
        res = [t.__name__ for t in types]
    elif isinstance(types, type):
        res = '\'' + types.__name__ + '\''
    elif isinstance(types, str):
        res = '\'' + types + '\''
    else:
        res = '[INVALID]'
    return res


def values_to_str(values):
    if isinstance(values, (tuple, list)):
        res = [v.__name__ for v in values]
    elif isinstance(values, type):
        res = '\'' + str(values) + '\''
    elif isinstance(values, str):
        res = '\'' + values + '\''
    else:
        res = values
    return res

# ############################################################### #


def create_set(values):
    def add(_set, _elem):
        _set.add(_elem)
        return _set
    return reduce(add, values, set())

# ############################################################### #
# ############################################################### #


class CheckerException(Exception):

    """ Ratpy Checker Exception class """

# ############################################################### #
# ############################################################### #


class CheckerItem(namedtuple('CheckerItem', ['name', 'types', 'default'])):

    """ Ratpy Checker Item class """

    # ####################################################### #
    # ####################################################### #

    def __init__(self, *args, **kwargs):

        super().__init__()
        self.hash = hash(self.name)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return (self.hash == other.hash) if isinstance(other, self.__class__) else NotImplemented

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class CheckerItemParams(namedtuple('CheckerItemParams', ['types', 'default'])):

    """ Ratpy Checker Item Parameters class """

# ############################################################### #
# ############################################################### #


class CheckerItemsSet(set):

    """ Ratpy Items Set class """

    # ####################################################### #
    # ####################################################### #

    def __str__(self):
        return str([m.name for m in self])

    # ####################################################### #

    def add(self, elem):
        if elem is None:
            pass
        elif isinstance(elem, CheckerItem):
            set.add(self, elem)
        elif isinstance(elem, tuple) and len(elem) == 2:
            set.add(self, CheckerItem(elem[0], elem[1].types, elem[1].default))
        elif isinstance(elem, tuple) and len(elem) == 3:
            set.add(self, CheckerItem(elem))

    def to_dict(self):
        return { m.name: CheckerItemParams(m.types, m.default) for m in self }

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #


class Checker(Logger):

    """ Ratpy Checker """

    # ####################################################### #
    # ####################################################### #

    def __init__(self, *args, **kwargs):
        Logger.__init__(self, *args, **kwargs)

    # ####################################################### #

    def _invalid_name(self, name, valid_names):
        self.logger.error('INVALID NAME ! [%s] USE NAMES IN %s', name, valid_names)
        raise CheckerException()

    def _invalid_type(self, element, name, types):
        self.logger.error('INVALID TYPE ! USE TYPE(S) %s FOR \'%s\' %s', types_to_str(types), name, element.upper())

    def _invalid_value(self, element, name, values):
        self.logger.error('INVALID VALUE ! USE VALUE(S) %s FOR \'%s\' %s', values_to_str(values), name, element.upper())

    def _success(self, element, name, value):
        self.logger.debug('{:_<18} : OK   [%s: %s]'.format('User '+element), name, value.__class__.__name__)

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
