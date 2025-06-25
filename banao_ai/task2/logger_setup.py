import logging
import sys

def set_logger():
    """Sets up a logger for the ClassificationDAG module."""
    
    logger = logging.getLogger("ClassificationDAG_Logger")
    logger.setLevel(logging.INFO)
    
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler("log_file.log")
    file_handler.setFormatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = set_logger()

