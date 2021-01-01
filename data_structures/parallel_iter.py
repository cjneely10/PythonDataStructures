"""
Module has various decorators to parallelize function/method calls
"""
import asyncio
from typing import Callable, Dict, List, Optional


def parallelize(input_dict: Dict[str, List[object]]):
    """ Parallelize function call using provided kwargs input dict. All non-kwargs
    are not adjusted. Expected input is dict mapping to list of inputs to try

    :param input_dict: arg_name: List[inputs...]
    :raises: AttributeError for improperly formatted input data
    :return: Decorated function
    """
    # Validate input dict when code is read in
    _validate_input_dict(input_dict)

    def decorator(func: Callable):
        def fxn(*args, **kwargs):
            args = list(args)
            return asyncio.run(_runner(input_dict, func, args, kwargs))

        return fxn

    return decorator


async def _runner(input_dict: Dict[str, List[object]], fxn_to_call: Callable,
                  args: List[object], kwargs: Dict[str, object]) -> List[Optional[object]]:
    """ Build list of function calls and call each

    :param input_dict: Input kwargs for generating function calls
    :param fxn_to_call: Function to call
    :param args: Args to pass to function call
    :param kwargs: Kwargs to pass to function, some may be edited per request at decoration
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
    return list(res)


async def _caller(fxn: Callable, args: List[object], kwargs: Dict[str, object]) -> Optional[object]:
    """ Call function with specified args and kwargs

    :param fxn: Function to call asynchronously
    :param args: Args passed to function
    :param kwargs: Amended kwargs passed to function
    :return: Result of function
    """
    res = await fxn(*args, **kwargs)
    return res


def _validate_input_dict(input_dict: Dict[str, List[object]]):
    """ Check dict of input passed at decorator level. Confirm that some data is passed (otherwise
    there is nothing to parallelize) and that the length of each input is that same

    :param input_dict: Input data to pass to functions
    :raises: AttributeError if improperly formatted data
    """
    if not isinstance(input_dict, dict):
        raise AttributeError("Input data must be in dict format")
    input_ids = tuple(input_dict.keys())
    if len(input_ids) == 0:
        raise AttributeError("Cannot parallelize without provided input options")
    _len = len(input_dict[input_ids[0]])
    for key in input_ids[1:]:
        if len(input_dict[key]) != _len:
            raise AttributeError("Input data sizes are not identical")
