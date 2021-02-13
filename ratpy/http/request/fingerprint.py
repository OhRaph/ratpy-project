""" Ratpy Request FingerPrint module"""

import hashlib
import weakref
from w3lib.url import canonicalize_url  # pylint: disable=import-error

from ratpy.utils import to_bytes

# ############################################################### #
# ############################################################### #

REQUEST_FINGERPRINT_CACHE = weakref.WeakKeyDictionary()

# ############################################################### #


def request_fingerprint(request):

    cache = REQUEST_FINGERPRINT_CACHE.setdefault(request, {})
    cache_key = (request.method, str(request.timestamp), tuple(to_bytes(h.lower()) for h in sorted(request.cb_kwargs)))
    if cache_key not in cache:
        _fp = hashlib.sha1()
        _fp.update(to_bytes(canonicalize_url(request.url, keep_fragments=False, keep_blank_values=False)))
        _fp.update(to_bytes(str(request.timestamp)))
        _fp.update(request.body or b'')
        cache[cache_key] = _fp.hexdigest()
    return cache[cache_key]

# ############################################################### #
# ############################################################### #
