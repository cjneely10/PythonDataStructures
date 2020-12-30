"""
Module holds class TypeChecker for simple function type check at runtime prior to function call
"""
import inspect
from typing import get_type_hints, Callable, Set, Type, Union


class TypeChecker:
    """
    Class TypeChecker has simple decorator method to check if function has been called with specified parameters
    and to handle type checking if not yet called
    """
    # Cache
    _checked: Set[int] = set()
    # Default error string
    ERR_STR = "Data <{}>\nmust be of type {}"

    @staticmethod
    def check_types(f: Callable):
        """ Check if types of args/kwargs passed to function/method are valid for provided type signatures

        :param f: Called function/method
        :return: Decorated functino/method. Raises TypeError if improper type/arg combination is found
        """
        def func(self, *args, **kwargs):
            # Get passed args as dict
            passed_args = inspect.signature(f).bind(self, *args, **kwargs).arguments
            # Check cache
            if TypeChecker._is_cached(id(passed_args)):
                return f(self, *args, **kwargs)
            # Get allowed types of f
            specified_types = get_type_hints(f)
            for arg_name, arg_type in specified_types.items():
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
            TypeChecker._checked.add(id(passed_args))
            return f(self, *args, **kwargs)

        return func

    @staticmethod
    def _is_cached(_id: int) -> bool:
        """ Check if arguments dictionary id is already cached

        :param _id: id of arguments parsed to dict
        :return: In-cache status
        """
        return _id in TypeChecker._checked

    @staticmethod
    def _check_union(arg_type: Union, passed_value: object):
        for avail_arg in arg_type.__args__:
            if isinstance(passed_value, avail_arg):
                return True
        return False
