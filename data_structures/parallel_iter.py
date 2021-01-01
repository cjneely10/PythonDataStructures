"""
Module has various decorators for parallelizing function/method calls
"""
import asyncio
from typing import Callable, Dict, List, Tuple, Optional


def parallelize(input_dict: Dict[str, List[object]]):
    """ Parallelize function call using provided kwargs input dict. All non-kwargs
    are not adjusted. Expected input is dict mapping to list of inputs to try

    :param input_dict: arg_name: List[inputs...]
    :return: Decorated function
    """
    def decorator(func: Callable):
        def fxn(*args, **kwargs):
            args = list(args)
            return asyncio.run(_runner(input_dict, func, args, kwargs))

        return fxn

    return decorator


async def _runner(input_dict: Dict[str, List[object]], fxn_to_call: Callable, args: List, kwargs: Dict) -> Tuple:
    """ Build list of function calls and call each

    :param input_dict: Input kwargs for generating function calls
    :param fxn_to_call: Function to call
    :param args: Args to pass to function call
    :param kwargs: kwargs to pass to function, some may be edited per request at decoration
    :return: Results of calling all functions
    """
    pos = 0
    fxn_call_list = []
    at_outer = False
    while at_outer is False:
        arg_combo = {**kwargs}
        for key in input_dict.keys():
            if pos == len(input_dict[key]) - 1:
                at_outer = True
            arg_combo[key] = input_dict[key][pos]
        fxn_call_list.append((fxn_to_call, arg_combo))
        pos += 1
    res = await asyncio.gather(*(_caller(fxn, args, kw_combo) for fxn, kw_combo in fxn_call_list))
    return res


async def _caller(fxn: Callable, args: List, kwargs: Dict) -> Optional[object]:
    """ Call function with specified args and kwargs

    :param fxn: Function to call asynchronously
    :param args: Args passed to function
    :param kwargs: Amended kwargs passed to function
    :return: Result of function
    """
    res = await fxn(*args, **kwargs)
    return res
