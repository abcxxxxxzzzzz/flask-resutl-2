loggers_format = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        "simple": {"format": "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)ss"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "logs/info.log",
            "maxBytes": 10485760,
            "backupCount": 50,
            "encoding": "utf8",
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8",
        },
        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "logs/debug.log",
            "maxBytes": 10485760,
            "backupCount": 50,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "my_module": {"level": "ERROR", "handlers": ["console"], "propagate": "no"}
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["error_file_handler", "debug_file_handler"],
    },
}
