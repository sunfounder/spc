import logging
from logging.handlers import RotatingFileHandler
import os

class Logger(object):
    LOG_FOLDER="/opt/spc/log"

    def __init__(self, script_name="CORE", maxBytes=10*1024*1024, backupCount=10):
        self.script_name = script_name
        self.log_path = os.path.join(self.LOG_FOLDER, f"{self.script_name.lower()}.log")
        self.logger = logging.getLogger(self.script_name)
        self.logger.setLevel(logging.DEBUG)

        if not os.path.exists(os.path.dirname(self.log_path)):
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # Create a handler, used for output to a file
        file_handler = RotatingFileHandler(self.log_path, maxBytes=maxBytes, backupCount=backupCount)
        file_handler.setLevel(logging.DEBUG)

        # Create a handler, used for output to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Define the output format of handler
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(name)s][%(levelname)s] %(message)s', datefmt='%y/%m/%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def __call__(self, msg: str = None, level='DEBUG'):
        if level == 'DEBUG':
            self.logger.debug(msg)
        elif level == 'INFO':
            self.logger.info(msg)
        elif level == 'WARNING':
            self.logger.warning(msg)
        elif level == 'ERROR':
            self.logger.error(msg)
        elif level == 'CRITICAL':
            self.logger.critical(msg)
