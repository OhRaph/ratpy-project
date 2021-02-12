""" Ratpy Request Serialization module """

import inspect

from ratpy.utils import to_unicode, load_object
from ratpy.http.request import Request

# ############################################################### #
# ############################################################### #


def request_to_dict(request, spider=None):

    if request is None:
        return None

    callback = request.callback
    if callable(callback):
        callback = _find_method(spider, callback)

    errback = request.errback
    if callable(errback):
        errback = _find_method(spider, errback)

    res = {
        'url': to_unicode(request.url),
        'callback': callback,
        'errback': errback,
        'method': request.method,
        'headers': dict(request.headers),
        'body': request.body,
        'cookies': request.cookies,
        'meta': request.meta,
        'encoding': request.encoding,
        'priority': request.priority,
        'timestamp': request.timestamp,
        'dont_filter': request.dont_filter,
        'flags': request.flags,
        'cb_kwargs': request.cb_kwargs
    }
    if type(request) is not Request:
        res['_class'] = request.__module__ + '.' + request.__class__.__name__
    return res

# ############################################################### #


def request_from_dict(dic, spider=None):

    if dic is None or dic == {}:
        return None

    callback = dic['callback']
    if callback and spider:
        callback = _get_method(spider, callback)

    errback = dic['errback']
    if errback and spider:
        errback = _get_method(spider, errback)

    request_cls = load_object(dic['_class']) if '_class' in dic else Request
    return request_cls(
        url=to_unicode(dic['url']),
        callback=callback,
        errback=errback,
        method=dic['method'],
        headers=dic['headers'],
        body=dic['body'],
        cookies=dic['cookies'],
        meta=dic['meta'],
        encoding=dic['encoding'],
        priority=dic['priority'],
        timestamp=dic['timestamp'],
        dont_filter=dic['dont_filter'],
        flags=dic.get('flags'),
        cb_kwargs=dic.get('cb_kwargs')
    )

# ############################################################### #
# ############################################################### #


def _find_method(obj, func):
    if obj:
        try:
            func_self = func.__self__
        except AttributeError:
            pass
        else:
            if func_self is obj:
                members = inspect.getmembers(obj, predicate=inspect.ismethod)
                for name, obj_func in members:
                    if obj_func.__func__ is func.__func__:
                        return name
    print('Function {} is not a method of : {}'.format(func, obj))
    raise ValueError('Function {} is not a method of : {}'.format(func, obj))

# ############################################################### #


def _get_method(obj, name):
    name = str(name)
    try:
        return getattr(obj, name)
    except AttributeError:
        pass
    print('Method {} not found in : {}'.format(name, obj))
    raise ValueError('Method {} not found in : {}'.format(name, obj))

# ############################################################### #
# ############################################################### #
