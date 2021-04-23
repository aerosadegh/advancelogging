"""
Advanced Logging
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import gzip
__version__ = '0.5'

_log_format = '%(asctime)s - (%(name)s) %(levelname)-8s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s'


_filename = 'app.log'
_loglvl = logging.NOTSET

#  Level    |Numeric value
# -----------------------
# |CRITICAL |50
# |ERROR    |40
# |WARNING  |30
# |INFO     |20
# |DEBUG    |10
# |NOTSET   | 0


class MyRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, **kws):
        backupCount = kws.get('backupCount', 0)
        self.backup_count = backupCount
        logging.handlers.RotatingFileHandler.__init__(self, filename, **kws)

    def doArchive(self, old_log):
        with open(old_log) as log:
             with gzip.open(old_log + '.gz', 'wb') as comp_log:
                 comp_log.writelines(map(lambda x: bytes(x, "utf8"), log.readlines()))
        os.remove(old_log)
        
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = "%s.%d.gz" % (self.baseFilename, i)
                dfn = "%s.%d.gz" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)

                    # rename(sfn -> dfn)
                    with gzip.open(sfn, "rb") as s, gzip.open(dfn, "wb") as d:
                        d.writelines(s.readlines())
                    
                    os.remove(sfn)
        
        dfn = self.baseFilename + f".1"
        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            self.doArchive(dfn)
        if not self.delay:
            self.stream = self._open()
            



def get_stream_handler(loglvl=logging.INFO, format=None):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(loglvl)
    stream_handler.setFormatter(logging.Formatter(_log_format if not format else format))
    return stream_handler


def get_logger(name, 
               loglvl_stream=logging.INFO, format_stream=None,
               filename=None, maxByte=80000000, backupCount=None):

    logging.basicConfig(
        handlers=[MyRotatingFileHandler(_filename if not filename else filename,   # file log baseName,
                                        maxBytes=maxByte,                          # 80MB for each raw file,
                                        backupCount=backupCount)],                 # 8 file will be keep
        format= _log_format,
        level=_loglvl,
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    logger = logging.getLogger(name)
    # logger.setLevel(loglvl)
    logger.addHandler(get_stream_handler(loglvl_stream, format=format_stream))
    return logger


def get_funcs(name="MyLogger",
              loglvl_stream=logging.INFO, format_stream=None,
              filename=None, maxByte=None, backupCount=None):    
    _logger = get_logger(name, loglvl_stream, format_stream, filename, maxByte, backupCount)

    log = _logger.info
    logerr = _logger.error
    logdbg = _logger.debug
    logwrn = _logger.warning
    return log, logdbg, logwrn, logerr


 
if __name__ == "__main__":
    
    log, logdbg, logwrn, logerr = get_funcs("MyLOGGER")
    
    a = 5
    b = 0
    log('This is an info message')
    try:
        c = a / b
    except Exception as e:
        logerr(f"Exception occurred {e}", exc_info=True)
        
    logdbg("This is a debug msg!")


