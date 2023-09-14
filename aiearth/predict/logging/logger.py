import os
import logging


def setup_logger(
    logging_name: str,
    logging_level: int,
    logging_format: str,
):
    """Setup default logging"""
    logger = logging.getLogger(logging_name)
    if type(logging_level) is str:
        logging_level = logging.getLevelName(logging_level.upper())
    logger.setLevel(logging_level)

    default_handler = logging.StreamHandler()
    default_handler.setFormatter(logging.Formatter(logging_format))
    logger.addHandler(default_handler)

    log_dir = os.environ.get("AIE_PREDICT_LOG_DIR")
    if log_dir:
        log_path = os.path.join(log_dir, "app.log")
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(logging_format))
        logger.addHandler(file_handler)

    # Setting this will avoid the message
    # being propagated to the parent logger.
    logger.propagate = False


def get_root_logger(logging_name):
    return logging.getLogger(logging_name)


root_logging = "aie-predict"
logging_level = logging.INFO
logging_format = (
    "%(levelname)s %(asctime)s %(process)d %(filename)s:%(lineno)d - %(message)s"
)
setup_logger(root_logging, logging_level, logging_format)

root_logger = get_root_logger(root_logging)
