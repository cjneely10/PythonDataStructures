"""
Module holds class TypeChecker for simple function type check at runtime prior to function call
"""
import inspect
from typing import get_type_hints, Callable, Union, Dict


class TypeChecker:
    """
    Class TypeChecker has simple decorator method to check if function has been called with specified parameters
    and to handle type checking if not yet called
    """
    # Default error string
    ERR_STR = "Data {}\nmust be of type {}"
    _max_cache_size = 256
    _cache = set()

    @staticmethod
    def check_types(func: Callable):
        """ Check if types of args/kwargs passed to function/method are valid for provided type signatures

        :param func: Called function/method
        :return: Decorated function/method. Raises TypeError if improper type/arg combination is found
        """

        def fxn(*args, **kwargs):
            TypeChecker._clear_if_surpassed_max_size()
            # Get passed args as dict
            passed_args = inspect.signature(func).bind(*args, **kwargs).arguments
            # Get allowed types of f
            specified_types = get_type_hints(func)
            cache_add = id([*args, *kwargs, func.__name__])
            if cache_add not in TypeChecker._cache:
                for arg_name, arg_type in specified_types.items():
                    if arg_name not in passed_args.keys():
                        continue
                    TypeChecker._check_type(arg_type, arg_name, passed_args)
                TypeChecker._cache.add(cache_add)
            output = func(*args, **kwargs)
            if "return" in specified_types.keys():
                arg_type = specified_types["return"]
                if getattr(arg_type, "__args__", None) is not None:
                    if not TypeChecker._check_union(arg_type, output):
                        raise TypeError("return type does not match {}".format(" or ".join(list(map(str, arg_type)))))
                    # Type is a non-Union
                else:
                    if not isinstance(output, arg_type):
                        raise TypeError("return type does not match {}".format(" or ".join(list(map(str, arg_type)))))

            return output

        return fxn

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
    def _check_type(arg_type, arg_name: str, passed_args: Dict):
        """ Check if argument is proper type. Raises TypeError if improper

        :param arg_type: Type expected
        :param arg_name: Name of argument
        :param passed_args: Argument:Value dictionary
        """
        # Type may be a Union
        if getattr(arg_type, "__args__", None) is not None:
            if not TypeChecker._check_union(arg_type, passed_args[arg_name]):
                raise TypeError(
                    TypeChecker.ERR_STR.format(arg_name, " or ".join(list(map(str, arg_type.__args__))))
                )
        # Type is a non-Union
        else:
            if not isinstance(passed_args[arg_name], arg_type):
                raise TypeError(TypeChecker.ERR_STR.format(arg_name, " or ".join(list(map(str, arg_type)))))

    @staticmethod
    def clear_cache():
        """ Clear current cache contents

        """
        TypeChecker._cache = set()

    @staticmethod
    def current_cache_size() -> int:
        """ Get number of function call types stored in cache

        :return: Current number of call types stored in cache
        """
        return len(TypeChecker._cache)

    @staticmethod
    def set_max_cache_size(max_size: int):
        """ Set max cache. If current cache size exceeds max_size, current cache is cleared

        :param max_size: Number > 0 of cached checked-function calls to store
        """
        if isinstance(max_size, int) and max_size > 0:
            TypeChecker._max_cache_size = max_size
            return
        raise TypeError("Must provide positive cache size")

    @staticmethod
    def _clear_if_surpassed_max_size():
        """ Check if cache size surpasses largest allowed and clear

        """
        if TypeChecker.current_cache_size() >= TypeChecker._max_cache_size:
            TypeChecker.clear_cache()
