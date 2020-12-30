"""
Module holds class TypeChecker for simple function type check at runtime prior to function call
"""
import inspect
from functools import lru_cache
from typing import get_type_hints, Callable, Union


class TypeChecker:
    """
    Class TypeChecker has simple decorator method to check if function has been called with specified parameters
    and to handle type checking if not yet called
    """
    # Default error string
    ERR_STR = "Data {}\nmust be of type {}"

    @staticmethod
    @lru_cache(None, True)
    def check_types(func: Callable):
        """ Check if types of args/kwargs passed to function/method are valid for provided type signatures

        :param func: Called function/method
        :return: Decorated function/method. Raises TypeError if improper type/arg combination is found
        """
        def fxn(*args, **kwargs):
            # Get passed args as dict
            passed_args = inspect.signature(func).bind(*args, **kwargs).arguments
            # Get allowed types of f
            specified_types = get_type_hints(func)
            for arg_name, arg_type in specified_types.items():
                if arg_name not in passed_args.keys():
                    continue
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
            return func(*args, **kwargs)

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
