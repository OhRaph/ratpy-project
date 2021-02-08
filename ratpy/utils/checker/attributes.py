""" Ratpy Attribute module """

from functools import reduce

from ratpy.utils.checker import CheckerException, CheckerItem, CheckerItemParams, CheckerItemsSet, Checker, create_set

__all__ = ['AttributeException', 'Attribute', 'AttributeParams', 'AttributesSet', 'AttributesChecker']

# ############################################################### #
# ############################################################### #


class AttributeException(CheckerException):

    """ Ratpy Attribute Exception """

# ############################################################### #


class Attribute(CheckerItem):

    """ Ratpy Attribute class """

# ############################################################### #


class AttributeParams(CheckerItemParams):

    """ Ratpy Attribute Params class """

# ############################################################### #


class AttributesSet(CheckerItemsSet):

    """ Ratpy Attributes Set class """

# ############################################################### #


class AttributesChecker(Checker):

    """ Ratpy Attributes Checker class """

    # ####################################################### #
    # ####################################################### #

    _possible_attributes_cache = None
    _attributes_cache = None

    # ####################################################### #

    def __init__(self, *args, **kwargs):
        Checker.__init__(self, *args, **kwargs)

    # ####################################################### #
    # ####################################################### #

    @property
    def _possible_attributes(self):
        if self._possible_attributes_cache is None:
            self._possible_attributes_cache = self.__class__.possible_attributes().to_dict()
        return self._possible_attributes_cache

    @staticmethod
    def possible_attributes():
        return AttributesSet()

    # ####################################################### #

    def _check_attribute(self, attribute_name):
        return hasattr(self, attribute_name)

    # ####################################################### #

    @property
    def _attributes(self):
        if self._attributes_cache is None:
            self._attributes_cache = {}
            for attribute_name, attribute_params in self._possible_attributes.items():
                if self._check_attribute(attribute_name):
                    self._attributes_cache[attribute_name] = attribute_params
        return self._attributes_cache

    @property
    def attributes(self):
        return create_set(self._attributes)

    # ####################################################### #

    def get_attribute(self, attribute_name, attribute_default_value=None):

        attribute_value = None
        if attribute_name in self._possible_attributes:

            attribute_value_types = self._possible_attributes[attribute_name].types
            if not isinstance(attribute_default_value, attribute_value_types):
                if attribute_default_value is not None:
                    self._invalid_type('attribute default value', attribute_name, attribute_value_types)
                attribute_default_value = self._possible_attributes[attribute_name].default

            if attribute_name in self._attributes:

                attribute_value = getattr(self, attribute_name)
                if not isinstance(attribute_value, attribute_value_types):
                    if attribute_value is not None:
                        self._invalid_type('attribute value', attribute_name, attribute_value_types)
                    attribute_value = attribute_default_value
                else:
                    self._success('attribute', attribute_name, attribute_value)
            else:
                attribute_value = attribute_default_value
        else:
            self._invalid_name(attribute_name, self._possible_attributes.keys())
        return attribute_value

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #
