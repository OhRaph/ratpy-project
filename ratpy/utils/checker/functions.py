""" Ratpy Function module """

from functools import reduce

from ratpy.utils.checker import CheckerException, CheckerItem, CheckerItemParams, CheckerItemsSet, Checker, create_set

__all__ = ['FunctionException', 'Function', 'FunctionParams', 'FunctionsSet', 'FunctionsChecker']

# ############################################################### #
# ############################################################### #


class FunctionException(CheckerException):

    """ Ratpy Function Exception """

# ############################################################### #


class Function(CheckerItem):

    """ Ratpy Function class """

# ############################################################### #


class FunctionParams(CheckerItemParams):

    """ Ratpy Function Params class """


# ############################################################### #

class FunctionsSet(CheckerItemsSet):

    """ Ratpy Functions Set class """

# ############################################################### #


class FunctionsChecker(Checker):

    """ Ratpy Functions Checker class """

    # ####################################################### #
    # ####################################################### #

    _possible_functions_cache = None
    _functions_cache = None

    # ####################################################### #

    def __init__(self, *args, **kwargs):
        Checker.__init__(self, *args, **kwargs)

    # ####################################################### #
    # ####################################################### #

    @property
    def _possible_functions(self):
        if self._possible_functions_cache is None:
            self._possible_functions_cache = self.__class__.possible_functions().to_dict()
        return self._possible_functions_cache

    @staticmethod
    def possible_functions():
        return FunctionsSet()

    # ####################################################### #

    def _check_function(self, function_name):
        if hasattr(self, function_name):
            function = getattr(self, function_name)
            if callable(function):
                return True
            else:
                self._invalid_type('function', function_name, 'callable')
        return False

    # ####################################################### #

    @property
    def _functions(self):
        if self._functions_cache is None:
            self._functions_cache = {}
            for function_name, function_params in self._possible_functions.items():
                if self._check_function(function_name):
                    self._functions_cache[function_name] = function_params
        return self._functions_cache

    @property
    def functions(self):
        return create_set(self._functions)

    # ####################################################### #

    def call_function(self, function_name, function_default_result, *args, **kwargs):

        function_result = None
        if function_name in self._possible_functions:

            function_result_types = self._possible_functions[function_name].types
            if not isinstance(function_default_result, function_result_types):
                self._invalid_type('function default result', function_name, function_result_types)
                function_default_result = self._possible_functions[function_name].default

            if function_name in self._functions:

                function = getattr(self, function_name)
                function_result = function(*args, **kwargs)
                if not isinstance(function_result, function_result_types):
                    if function_result is not None:
                        self._invalid_value('function result', function_name, function_result_types)
                    function_result = self._possible_functions[function_name].default
                else:
                    self._success('function', function_name, function_result)
            else:
                function_result = function_default_result
        else:
            self._invalid_name('function name', function_name, self._possible_functions.keys())
        return function_result

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
