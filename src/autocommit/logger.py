import logging
import os
from datetime import datetime

def get_logger(name="autocommit"):
    logger = logging.getLogger(name)
    if not logger.handlers:  # Prevent adding handlers multiple times
        logger.setLevel(logging.INFO)

        log_directory = ".log"
        os.makedirs(log_directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_directory, f"{name}_{timestamp}.log")

        file_handler = logging.FileHandler(log_filename)
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
