import inspect
from typing import get_type_hints, Callable, Set


class TypeChecker:
    _checked: Set[int] = set()

    @staticmethod
    def check_types(f: Callable):
        def func(self, *args, **kwargs):
            passed_args = inspect.signature(f).bind(self, *args, **kwargs).arguments
            if id(passed_args) in TypeChecker._checked:
                print("Using cached")
                return f(self, *args, **kwargs)
            print("Checking...")
            specified_types = get_type_hints(f)
            for arg_name, arg_type in specified_types.items():
                if getattr(arg_type, "__args__", None) is not None:
                    passed = False
                    for avail_arg in arg_type.__args__:
                        if isinstance(passed_args[arg_name], avail_arg):
                            passed = True
                            break
                    if not passed:
                        raise TypeError("Data <{}> must be of type {}".format(arg_name, " or ".join(
                            list(map(str, arg_type.__args__)))))
                else:
                    if not isinstance(passed_args[arg_name], arg_type):
                        raise TypeError(
                            "Data <{}> must be of type {}".format(arg_name, " or ".join(list(map(str, arg_type)))))
            TypeChecker._checked.add(id(passed_args))
            return f(self, *args, **kwargs)

        return func
