import logging
import getpass
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


class filelog(object):
    def __init__(self):
        user = getpass.getuser()
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.DEBUG)

        # file log
        log_filename = datetime.now().strftime("log/%Y-%m-%d.log")
        fileHandler = TimedRotatingFileHandler(
            log_filename, when='D', interval=1,
            backupCount=30, encoding='UTF-8', delay=False, utc=False)
        logger = logging.getLogger()
        BASIC_FORMAT_F = "%(asctime)s - %(levelname)s filename:%(filename)s module:%(module)s func:%(funcName)-8s line%(lineno)s : %(message)s"
        DATE_FORMAT_F = '%Y-%m-%d %H:%M'
        formatter = logging.Formatter(BASIC_FORMAT_F, DATE_FORMAT_F)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, level, msg):
        self.logger.log(level, msg)

    def setLevel(self, level):
        self.logger.setLevel(level)


class cmdlog(object):
    def __init__(self):
        user = getpass.getuser()
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.DEBUG)

        # cmd log
        BASIC_FORMAT_C = '%(asctime)8s %(levelname)- 8s in %(module)8s: %(message)s'
        DATE_FORMAT_C = '%Y-%m-%d %H:%M'
        formatter = logging.Formatter(BASIC_FORMAT_C, DATE_FORMAT_C)
        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)
        self.logger.addHandler(streamhandler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, level, msg):
        self.logger.log(level, msg)

    def setLevel(self, level):
        self.logger.setLevel(level)

    def disable(self):
        logging.disable(50)
