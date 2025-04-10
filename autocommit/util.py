from pathlib import Path
import os
from config import Config

from logger import get_logger

config = Config.get_instance()
logger = get_logger()

def is_main_file(file_path: str) ->  bool:
    is_main_file = any(file_path.startswith(folder) for folder in config.main_folders) and file_path.endswith(tuple(config.main_extensions))
    if (is_main_file):
        logger.info(f"{file_path} is a main file")
    return is_main_file

def is_attachment_file(file_path: str) -> bool:
    is_attachment_file = any(file_path.startswith(folder) for folder in config.attachment_folders) or file_path.endswith(tuple(config.attachment_extensions))
    if (is_attachment_file):
        logger.info(f"{file_path} is an attachment file")
    return is_attachment_file

def ignore_path(event_path: str) -> bool:
    ignore = False
    for relative_dir in config.excluded_dirs:
         absolute_dir = os.path.join(config.repo_path, relative_dir)
         ignore = ignore or event_path.startswith(absolute_dir)
    return ignore

def file_exists(file_path: str) -> bool:
    return Path(file_path).exists()
