"""
Logger for CorpusFlow.

@author: rookieblack
@date  : 2025-07-10
"""
import os
import json
import time
import logging
import inspect

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Colors.BLUE,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.MAGENTA
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, Colors.WHITE)}{log_message}{Colors.RESET}"

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, log_dir, log_filename, when='midnight', interval=1, backupCount=7, encoding='utf-8'):
        self.log_dir = log_dir
        self.log_filename = log_filename
        super().__init__(os.path.join(log_dir, log_filename), when=when, interval=interval, backupCount=backupCount, encoding=encoding)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        # Get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        time_tuple = time.localtime(t)

        # Determine the new log file name based on the current time
        daily_log_path = os.path.join(self.log_dir, "daily_backup")
        os.makedirs(daily_log_path, exist_ok=True)
        dfn = os.path.join(daily_log_path, f"{time.strftime('%Y%m%d', time_tuple)}_{self.log_filename}")

        # Rename the current log file
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)

        # Reset the base filename and open a new log file
        if not self.delay:
            self.stream = self._open()

        # Update the rollover time
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        self.rolloverAt = newRolloverAt

    def emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.shouldRollover(record):
                self.doRollover()
            TimedRotatingFileHandler.emit(self, record)
        except Exception:
            self.handleError(record)

class CustomJSONLogger:
    _instance = None

    @classmethod
    def get_instance(cls, log_dir="logs", log_filename="xapp.log", version="1.0", console_output=True):
        if cls._instance is None:
            cls._instance = cls(log_dir, log_filename, version, console_output)
        return cls._instance

    def __init__(self, log_dir="logs", log_filename="xapp.log", version="1.0", console_output=True):
        self.log_filename = log_filename
        self.default_version = version
        self.log_dir = log_dir

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)

        # Create a custom file handler with your specified format
        file_formatter = logging.Formatter('%(message)s')  # Log file output format!
        self.file_handler = CustomTimedRotatingFileHandler(
            log_dir=self.log_dir,
            log_filename=self.log_filename,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )
        self.file_handler.setFormatter(file_formatter)
        self.logger.addHandler(self.file_handler)

        # Create a console handler with the same format as the file handler
        if console_output:  # Only add console handler when needed
            console_formatter = ColoredFormatter('%(message)s')  # Console output format!
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def get_calling_class(self):
        current_frame = inspect.currentframe()
        calling_frame = inspect.getouterframes(current_frame, 2)
        calling_class = calling_frame[2].frame.f_locals.get('self', None)
        if calling_class:
            return calling_class.__class__.__name__
        return None
    
    def safe_str(self, obj):
        try:
            return str(obj)
        except UnicodeEncodeError:
            return obj.encode('utf-8', errors='ignore').decode('utf-8')

    def log(self, message, data=None, log_level=None, category=None, version=None, tags=None):
        if log_level is None:
            log_level = logging.DEBUG

        if category is None:
            category = self.get_caller_script_name()

        env = os.getenv('PROJ_ENV', 'dev')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        log_data = {
            'time': current_time,
            'version': version or self.default_version,
            'level': logging.getLevelName(log_level),
            'category': category,
            'tags': tags,
            'env': env,
            'message': {
                'text': self.safe_str(message) if isinstance(message, dict) else self.safe_str(message)
            }
        }

        if log_level == logging.ERROR:
            # Use findCaller to get correct lineno and pathname
            caller = self.logger.findCaller()
            log_data['message']['line'] = f"{caller[1]}:{caller[2]}"
            calling_class = self.get_calling_class()
            if calling_class:
                log_data['message']['classname'] = calling_class

        if data is not None:
            if isinstance(data, dict):
                log_data['message'].update(data)
            else:
                log_data['message']['data'] = data

        # Prepare JSON formatted log message for file handler
        json_log_message = json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))
        
        # Prepare formatted log message for console handler
        console_log_message = f"{log_data['time']} - {log_data['level']} - {log_data['category']}: {log_data['message']['text']}"
        
        # Record to file and console
        for handler in self.logger.handlers:
            if isinstance(handler, CustomTimedRotatingFileHandler):
                handler.emit(logging.LogRecord(
                    name=self.logger.name,
                    level=log_level,
                    pathname='',
                    lineno=0,
                    msg=json_log_message,
                    args=(),
                    exc_info=None
                ))
            elif isinstance(handler, logging.StreamHandler):
                handler.emit(logging.LogRecord(
                    name=self.logger.name,
                    level=log_level,
                    pathname='',
                    lineno=0,
                    msg=console_log_message,
                    args=(),
                    exc_info=None
                ))

    @staticmethod
    def get_caller_script_name():
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename
            if filename != __file__:
                return os.path.basename(filename)
            frame = frame.f_back
        return None

    def warning(self, message, data=None, category=None, version=None, tags=None):
        self.log(message, data, log_level=logging.WARNING, category=category, version=version, tags=tags)

    def error(self, message, data=None, category=None, version=None, tags=None):
        self.log(message, data, log_level=logging.ERROR, category=category, version=version, tags=tags)

    def exceptions(self, message, category=None, version=None, tags=None):
        self.log(message, log_level=logging.ERROR, category=category, version=version, tags=tags)

    def info(self, message, data=None, category=None, version=None, tags=None):
        self.log(message, data, log_level=logging.INFO, category=category, version=version, tags=tags)

    # Add success level, same as info level
    def success(self, message, data=None, category=None, version=None, tags=None):
        self.log(message, data, log_level=logging.INFO, category=category, version=version, tags=tags)

    def debug(self, message, data=None, category=None, version=None, tags=None):
        self.log(message, data, log_level=logging.DEBUG, category=category, version=version, tags=tags)

# Create a global logger instance
xlogger = CustomJSONLogger.get_instance()

# Define get_logger as a function
def get_logger():
    return xlogger

if __name__ == "__main__":
    xlogger.info("Hello, World!")