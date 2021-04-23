from logger import get_funcs


log, logdbg, logwrn, logerr = get_funcs("my Logger", maxByte=7000, backupCount=5, filename="mylogfile.log")



def log_deco(func):
    def wrapper(*args, **kwargs):
        kwst = ""
        for k in kwargs:
            kwst += f"{k}={kwargs[k]}, "

        try:
            log(f"Calling {func.__name__}{str(args).rstrip(') ')}, {kwst.strip(' ,')})...")
            res = func(*args, **kwargs)
        except Exception as e:
            logerr(f"Error Occurred: {e}", exc_info=True)
        else:
            log(f"Return {str(type(res)).strip('<>')[6:]}:> {res!r} ")
            return res

    return wrapper




@log_deco
def test_func(num, char, p=False, q=None):
    res = char*num
    if p:
        print(res)
        
    ### raise Handy Error
    if num<0:
        raise ValueError(f"num must be non-negative:(got {num})")

    return res


for i in range(-10, 50):
    test_func(i, "A", p=bool(i), q=i*2)