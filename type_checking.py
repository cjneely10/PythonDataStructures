"""
Module holds class TypeChecker for simple function type check at runtime prior to function call
"""
import inspect
from typing import get_type_hints, Callable, Set, Union


# TODO: Handle ForwardRef
class TypeChecker:
    """
    Class TypeChecker has simple decorator method to check if function has been called with specified parameters
    and to handle type checking if not yet called
    """
    # Default error string
    ERR_STR = "Data {}\nmust be of type {}"

    def __init__(self):
        # Cache
        self._checked: Set[int] = set()

    def check_types(self, func: Callable):
        """ Check if types of args/kwargs passed to function/method are valid for provided type signatures

        :param func: Called function/method
        :return: Decorated function/method. Raises TypeError if improper type/arg combination is found
        """
        def fxn(*args, **kwargs):
            # Get passed args as dict
            passed_args = inspect.signature(func).bind(*args, **kwargs).arguments
            # Check cache
            if self._is_cached(id(passed_args)):
                return func(*args, **kwargs)
            # Add to cache
            self._checked.add(id(passed_args))
            # Get allowed types of f
            specified_types = get_type_hints(func)
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
            return func(*args, **kwargs)

        return fxn

    def _is_cached(self, _id: int) -> bool:
        """ Check if arguments dictionary id is already cached

        :param _id: id of arguments parsed to dict
        :return: In-cache status
        """
        return _id in self._checked

    @staticmethod
    def _check_union(arg_type: Union, passed_value: object) -> bool:
        """ Check Union type annotation to see if passed value is one of the specified types

        :param arg_type: Union annotation
        :param passed_value: type of argument passed
        :return: Status if passed_value is valid based on contents of Union
        """
        for avail_arg_type in arg_type.__args__:
            if type(passed_value) == avail_arg_type:
                return True
        return False
