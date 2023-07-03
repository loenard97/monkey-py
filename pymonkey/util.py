from typing import Any, Callable, cast

FLOG_DEPTH = 0


def flog(func: Callable) -> Callable:
    def inner(*args: Any, **kwargs: Any) -> Any:
        global FLOG_DEPTH
        tab = " │  " * FLOG_DEPTH
        FLOG_DEPTH += 1

        arg_str = ", ".join([str(a) for a in args])
        kwarg_str = ", ".join([str(kw) for kw in kwargs])

        print(f"{tab}call '{func.__name__}'")
        if arg_str:
            print(f"{tab} ├─ args {arg_str}")
        if kwarg_str:
            print(f"{tab} ├─ kwargs {kwarg_str}")

        ret = func(*args, **kwargs)
        print(f"{tab} └─ return -> {ret}")
        FLOG_DEPTH -= 1
        return ret

    return inner


class MetaClass:
    pass


class Logger(type):
    @staticmethod
    def _decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            global FLOG_DEPTH
            tab = " │  " * FLOG_DEPTH
            FLOG_DEPTH += 1

            arg_str = ", ".join([str(a) for a in args])
            kwarg_str = ", ".join([str(kw) for kw in kwargs])

            print(f"{tab}call '{func.__name__}'")
            if arg_str:
                print(f"{tab} ├─ args {arg_str}")
            if kwarg_str:
                print(f"{tab} ├─ kwargs {kwarg_str}")

            ret = func(*args, **kwargs)
            print(f"{tab} └─ return -> {ret}")
            FLOG_DEPTH -= 1
            return ret

        return wrapper

    def __new__(cls: type[type], name: str, bases: tuple, attrs: dict) -> "Logger":
        for key in attrs.keys():
            if callable(attrs[key]):
                func = attrs[key]
                attrs[key] = Logger._decorator(func)

        return cast(Logger, type.__new__(cls, name, bases, attrs))
