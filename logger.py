import gzip
import logging
import os
from logging.handlers import RotatingFileHandler

__version__ = "0.8"

LOG_FORMAT = "%(asctime)s - (%(name)s) %(levelname)-8s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s"

FILENAME = "app.log"
LOG_LEVEL = logging.NOTSET

#  Level    |Numeric value
# -----------------------
# |CRITICAL |50
# |ERROR    |40
# |WARNING  |30
# |INFO     |20
# |DEBUG    |10
# |NOTSET   | 0


class MyRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, **kws):
        backupCount = kws.get("backupCount", 5)
        self.backup_count = backupCount
        super().__init__(filename, **kws)

    def doArchive(self, old_log):
        with open(old_log) as raw_log:
            with gzip.open(old_log + ".gz", "wb") as compressed_log:
                compressed_log.writelines(
                    map(lambda x: bytes(x, "utf8"), raw_log.readlines())
                )
        os.remove(old_log)

    def close_current_log_file(self):
        if self.stream:
            self.stream.close()
            self.stream = None

    def rename_old_log_files(self):
        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = f"{self.baseFilename}.{i}.gz"
                dfn = f"{self.baseFilename}.{i + 1}.gz"
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    with gzip.open(sfn, "rb") as s, gzip.open(dfn, "wb") as d:
                        d.writelines(s.readlines())
                    os.remove(sfn)

    def remove_excess_log_files(self):
        dfn = f"{self.baseFilename}.1"
        if os.path.exists(dfn):
            os.remove(dfn)
        return dfn

    def archive_old_log_file(self, dfn):
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            self.doArchive(dfn)

    def open_new_log_file(self):
        if not self.delay:
            self.stream = self._open()

    def doRollover(self):
        self.close_current_log_file()
        self.rename_old_log_files()
        dfn = self.remove_excess_log_files()
        self.archive_old_log_file(dfn)
        self.open_new_log_file()


class MyStreamHandler(logging.StreamHandler):
    def __init__(self, log_level=logging.INFO, format=None):
        super().__init__()
        self.setLevel(log_level)
        self.setFormatter(logging.Formatter(LOG_FORMAT if not format else format))


def get_logger(
    name,
    stream_log_level=logging.INFO,
    stream_log_format=LOG_FORMAT,
    file_log_format=LOG_FORMAT,
    file_log_level=logging.INFO,
    filename=FILENAME,
    maxByte=None,
    backupCount=None,
    stream_log_enabled=True,
):
    maxByte = maxByte or 1048576  # 1MB
    backupCount = backupCount or 5
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if filename:
        file_handler = MyRotatingFileHandler(
            filename,
            maxBytes=maxByte,
            backupCount=backupCount,
        )
        file_handler.setFormatter(logging.Formatter(file_log_format))
        file_handler.setLevel(file_log_level)
        logger.addHandler(file_handler)
    if stream_log_enabled:
        stream_handler = MyStreamHandler(stream_log_level)
        stream_handler.setFormatter(logging.Formatter(stream_log_format))
        logger.addHandler(stream_handler)

    return logger



if __name__ == "__main__":

    logger = get_logger("MyLOGGER")

    a = 5
    b = 0
    logger.info("This is an info message")
    try:
        c = a / b
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=True)

    logger.debug("This is a debug msg!")
