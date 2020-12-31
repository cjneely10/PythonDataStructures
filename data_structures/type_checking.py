"""
Module holds class TypeChecker for simple function type check at runtime prior to function call
"""
import inspect
from typing import get_type_hints, Callable, Union, Type


class TypeChecker:
    """
    Class TypeChecker has simple decorator method to check if function has been called with specified parameters
    and to handle type checking if not yet called
    """
    # Default error string
    ERR_STR = "Data %s must be of type {}"
    RETURN_ERR_STR = "return type does not match {}"
    _max_cache_size = 256
    _cache = set()

    @staticmethod
    def check_types(func: Callable):
        """ Check if types of args/kwargs passed to function/method are valid for provided type signatures

        :param func: Called function/method
        :raises: TypeError for improper arg/kwarg type combinations
        :return: Decorated function/method. Raises TypeError if improper type/arg combination is found
        """

        def fxn(*args, **kwargs):
            TypeChecker._clear_if_surpassed_max_size()
            # Get passed args as dict
            passed_args = inspect.signature(func).bind(*args, **kwargs).arguments
            # Get types specified by type annotations
            specified_types = get_type_hints(func)
            # Calculate id of function data
            cache_add_id = id([*args, *kwargs.values(), func.__module__, func.__name__])
            # Check if cached
            if cache_add_id not in TypeChecker._cache:
                # Check arguments passed to ensure valid
                for arg_name, arg_type in specified_types.items():
                    if arg_name not in passed_args.keys():
                        continue
                    TypeChecker._validate_type(arg_type, passed_args[arg_name], TypeChecker.ERR_STR % arg_name)
            # Get function output
            output = func(*args, **kwargs)
            # Confirm output is valid
            if "return" in specified_types.keys():
                TypeChecker._validate_type(specified_types["return"], output, TypeChecker.RETURN_ERR_STR)
            # Add successful call to cache
            TypeChecker._cache.add(cache_add_id)
            return output

        return fxn

    @staticmethod
    def _clear_if_surpassed_max_size():
        """ Check if cache size surpasses largest allowed and clear

        """
        if TypeChecker.get_current_cache_size() >= TypeChecker._max_cache_size:
            TypeChecker.clear_cache()

    @staticmethod
    def _check_union(arg_type: Union, passed_value: object) -> bool:
        """ Check Union type annotation to see if passed value is one of the specified types

        :param arg_type: Union annotation
        :param passed_value: type of argument passed
        :return: Status if passed_value is valid based on contents of Union
        """
        for avail_arg_type in arg_type.__args__:
            if isinstance(passed_value, avail_arg_type):
                return True
        return False

    @staticmethod
    def _validate_type(arg_type: Type, output: object, err_string: str):
        """ Check if arg type matches actual arg value, if not display error string

        :param arg_type: Expected type
        :param output: Actual value
        :param err_string: Error string to display if failed
        :raises: TypeError if improper type found
        """
        if getattr(arg_type, "__args__", None) is not None:
            if not TypeChecker._check_union(arg_type, output):
                raise TypeError(err_string.format(" or ".join(list(map(str, arg_type.__args__)))))
        else:
            if not isinstance(output, arg_type):
                raise TypeError(err_string.format(arg_type))

    @staticmethod
    def clear_cache():
        """ Clear current cache contents

        """
        TypeChecker._cache = set()

    @staticmethod
    def get_current_cache_size() -> int:
        """ Get number of function call types stored in cache

        :return: Current number of call types stored in cache
        """
        return len(TypeChecker._cache)

    @staticmethod
    def set_max_cache_size(max_size: int):
        """ Set max cache. If current cache size exceeds max_size, current cache is cleared

        :param max_size: Number > 0 of cached checked-function calls to store
        :raises: TypeError for improper arg/kwarg type combinations
        """
        if isinstance(max_size, int) and max_size > 0:
            TypeChecker._max_cache_size = max_size
            return
        raise TypeError("Must provide positive cache size")
