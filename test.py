from functools import wraps
import logging

from logger import get_logger


logger = get_logger(
    "my Logger",
    maxByte=7000,
    backupCount=5,
    filename="my_log.log",
)


def log_deco(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kw_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        arg_str = ", ".join(map(str, args))
        args_str = f"{arg_str}, {kw_str}".strip(", ")
        logger.info(f"Calling {func.__name__}({args_str})...")
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error Occurred: {e}", exc_info=True)
        else:
            logger.info(f"Return {type(res).__name__}: {res!r}")
            return res

    return wrapper


@log_deco
def test_func(num, char, p=False, q=None):
    res = char * num
    if p:
        print(res)

    ### raise Handy Error
    if num < 0:
        raise ValueError(f"num must be non-negative:(got {num})")

    return res


for i in range(-5, 50):
    # test_func(i, "A", p=bool(i), q=i * 2)
    pass
for iii in range(2):
    try:
        1 / 0
    except Exception as e:
        logger.error(f"{e} - {iii}", exc_info=True)
