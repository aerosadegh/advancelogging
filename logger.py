"""
Advanced Logging
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import gzip

__version__ = '0.2'
_filename = 'app.log'
_loglvl = logging.DEBUG


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
            
_c_handler = logging.StreamHandler()
_c_handler.setLevel(_loglvl)
_cformat = logging.Formatter('%(asctime)s - %(levelname)-8s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s',)
_c_handler.setFormatter(_cformat)
 

logging.basicConfig(
        handlers=[MyRotatingFileHandler(_filename,         # file log baseName,
                                        maxBytes=80000000, # 80MB for each raw file,
                                        backupCount=8)],   # 8 file will be keep
        level=_loglvl,
        format='%(asctime)s - %(levelname)-8s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')

_logger = logging.getLogger(__name__)

_logger.addHandler(_c_handler)

log = _logger.info
logerr = _logger.error
logdbg = _logger.debug
logwrn = _logger.warning


if __name__ == "__main__":
    a = 5
    b = 0
    log('This is an info message')
    try:
        c = a / b
    except Exception as e:
        logerr(f"Exception occurred {e}", exc_info=True)


