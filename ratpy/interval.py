""" Ratpy Interval module """

import re

# ############################################################### #
# ############################################################### #


def _convert(interval):
    search = re.search(r'^(\d*[dD])?(\d*[hH])?(\d*[mM])?(\d*[sS])?$', interval)
    res = 0
    res += (int(search.group(1)[0:-1]) if search.group(1) else 0) * 24 * 60 * 60
    res += (int(search.group(2)[0:-1]) if search.group(2) else 0) * 60 * 60
    res += (int(search.group(3)[0:-1]) if search.group(3) else 0) * 60
    res += (int(search.group(4)[0:-1]) if search.group(4) else 0)
    return res

# ############################################################### #


class Interval(int):

    """ Ratpy Interval class """

    # ####################################################### #
    # ####################################################### #

    cb_kwargs = None

    def __new__(cls, value, **kwargs):

        if isinstance(value, str):
            value = _convert(value)
        elif isinstance(value, int):
            value = max(value, 0)
        else:
            raise ValueError('Interval value must be string or integer')

        self = int.__new__(cls, value)
        self.cb_kwargs = kwargs
        return self

    def __call__(self, value=0):
        return Interval(self+value)

    def __str__(self):
        d = self / (24 * 60 * 60)
        h = self % (24 * 60 * 60) / (60 * 60)
        m = self % (24 * 60 * 60) % (60 * 60) / 60
        s = self % (24 * 60 * 60) % (60 * 60) % 60
        return '{}d{}h{}m{}s'.format(int(d), int(h), int(m), int(s))

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
