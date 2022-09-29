from flask import Flask
import logging.config
from .init_sqlalchemy import db, init_database, BaseModel
from .init_dotenv import init_dotenv
from .init_log import loggers_format
from .init_GoogleAuthenticator import init_google
from .init_Redis import init_redis, Redis




def init_plugs(app: Flask) -> None:
    init_database(app)
    init_dotenv()
    logging.config.dictConfig(loggers_format)
    init_google()
    init_redis()
