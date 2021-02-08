""" Ratpy Response FingerPrint module"""

import hashlib
import weakref
from w3lib.url import canonicalize_url  # pylint: disable=import-error

from ratpy.utils import to_bytes

# ############################################################### #
# ############################################################### #

RESPONSE_FINGERPRINT_CACHE = weakref.WeakKeyDictionary()

# ############################################################### #


def response_fingerprint(response):

    cache = RESPONSE_FINGERPRINT_CACHE.setdefault(response.request, {})
    cache_key = (response.request.method, tuple(to_bytes(h.lower()) for h in sorted(response.request.cb_kwargs)))
    if cache_key not in cache:
        _fp = hashlib.sha1()
        _fp.update(to_bytes(canonicalize_url(response.request.url, keep_fragments=False, keep_blank_values=False)))
        _fp.update(response.body or b'')
        cache[cache_key] = _fp.hexdigest()
    return cache[cache_key]

# ############################################################### #
# ############################################################### #
