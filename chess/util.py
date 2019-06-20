from functools import wraps


def collect(collector):
    """
    Wraps a generator inside a collector function.

    Used to get rid of boilerplate method pairs like these:

    >>> def number_cube(n) -> str:
    ...     return ''.join(_number_cube(n))
    ...
    ... def _number_cube(n) -> Generator[str]:
    ...     for i in range(n**2):
    ...         yield str(i)
    ...         if (i + 1) % n == 0:
    ...             yield ''\n''

    Instead, use this decorator:

    >>> concatenate = collect(lambda g: ''.join(g))
    ...
    ... @concatenate
    ... def number_cube(n) -> str:
    ...     for i in range(n**2):
    ...         yield str(i)
    ...         if (i + 1) % n == 0:
    ...             yield ''\n''
    """
    def decorator(generator):
        @wraps(generator)
        def wrapper(*args, **kwargs):
            return collector(generator(*args, **kwargs))
        return wrapper

    return decorator


concatenate = collect(lambda g: ''.join(g))
