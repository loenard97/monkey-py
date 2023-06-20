FLOG_DEPTH = 0


def flog(func):
    
    def inner(*args, **kwargs):
        global FLOG_DEPTH
        tab = ' │  ' * FLOG_DEPTH
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
