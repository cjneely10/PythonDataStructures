"""
Module has various decorators to parallelize function/method calls
"""
import asyncio
import concurrent.futures
from typing import Callable, Dict, List, Optional, Sequence, Iterable, Union

InputSequence = Sequence


def iter_threaded(threads: int, ignore_types: Optional[Iterable[Union[type, None]]] = None, **kwargs: InputSequence):
    """ Parallelize function call using provided kwargs input dict.
    All args/kwargs not provided are not adjusted.
    Each kwarg passed is expected to be a subclass of Sequence, and all kwargs are expected to have the
    same input length.

    Uses concurrent.futures and broadcasts calls across multiple threads

    :param threads: Number of threads to launch to complete task list
    :param ignore_types: Iterable of return types/Exception types to handle in parallelized call
    :param kwargs: Keyword arguments to override in function
    :raises: AttributeError for improperly formatted input data
    :return: Generator over results from each parallelized function call (in order)
    """
    if not isinstance(threads, int) or threads <= 0:
        raise TypeError("Must pass positive thread value")
    # Validate input dict when code is read in
    _validate_input_dict(kwargs)
    if ignore_types is not None:
        ignore_types = {_type
                        if isinstance(_type, type) else type(_type)
                        for _type in ignore_types}
    else:
        ignore_types = {}

    def decorator(func: Callable):
        def fxn(*args, **kws):
            fxn_call_list = _build_call_list(kwargs, kws)
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                output_data_futures = [executor.submit(func, *args, **arg_combo) for arg_combo in fxn_call_list]
                concurrent.futures.wait(output_data_futures)
                for output in output_data_futures:
                    # Goal is to catch all broad exceptions
                    try:
                        result = output.result()
                        if type(result) in ignore_types:
                            continue
                        yield result
                        # pylint: disable=broad-except
                    except BaseException as err:
                        if type(err) in ignore_types:
                            continue
                        raise type(err) from err

        return fxn

    return decorator


def iter_async(**kwargs: InputSequence):
    """ Parallelize function call using provided kwargs input dict. All non-kwargs
    are not adjusted. Expected input is dict mapping to list of inputs to try.

    Must decorate an async def function for valid functionality

    Uses asyncio and maintains call running over single thread

    :param kwargs: Keyword arguments to override in function
    :raises: AttributeError for improperly formatted input data
    :return: Decorated function
    """
    # Validate input dict when code is read in
    _validate_input_dict(kwargs)

    def decorator(func: Callable):
        def fxn(*args, **kws):
            args = list(args)
            return asyncio.run(_runner(kwargs, func, args, kws))

        return fxn

    return decorator


def _validate_input_dict(input_dict: Dict[str, InputSequence]):
    """ Check dict of input passed at decorator level. Confirm that some data is passed (otherwise
    there is nothing to parallelize) and that the length of each input is that same

    :param input_dict: Input data to pass to functions
    :raises: AttributeError if improperly formatted data
    """
    input_ids = tuple(input_dict.keys())
    _len = len(input_dict[input_ids[0]])
    for key in input_ids[1:]:
        if len(input_dict[key]) != _len:
            raise AttributeError("Input data sizes are not identical")


def _build_call_list(input_dict: Dict[str, InputSequence], kwargs: Dict[str, object]) -> List[Dict[str, object]]:
    """ Iterate over passed args to generate function call. Check lengths of args to make sure
    they are all the same

    :param input_dict: Reference to passed data
    :param kwargs: **kwargs
    :return: Function args calls as list
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
        fxn_call_list.append(arg_combo)
        pos += 1
    return fxn_call_list


async def _runner(input_dict: Dict[str, InputSequence], fxn_to_call: Callable,
                  args: List[object], kwargs: Dict[str, object]) -> List[Optional[object]]:
    """ Build list of function calls and call each

    :param input_dict: Input kwargs for generating function calls
    :param fxn_to_call: Function to call
    :param args: Args to pass to function call
    :param kwargs: Kwargs to pass to function, some may be edited per request at decoration
    :return: Results of calling all functions
    """
    fxn_call_list = _build_call_list(input_dict, kwargs)
    res = await asyncio.gather(*(_caller(fxn_to_call, args, kw_combo) for kw_combo in fxn_call_list))
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
