import inspect
import logging

from app.config import settings

logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)


class CustomLogger:
    @staticmethod
    def create_log(log_type: str, message: str):
        frame = inspect.currentframe().f_back
        filename = frame.f_globals["__file__"]
        app_index = filename.find("app/")
        if app_index != -1:
            filename = "/" + filename[app_index:]
        log_message = f"{filename}: {message}"

        if log_type == "debug":
            logger.debug(log_message)
        elif log_type == "warning":
            logger.warning(log_message)
        elif log_type == "error":
            logger.error(log_message)
        elif log_type == "critical":
            logger.critical(log_message)
        else:
            logger.info(log_message)
