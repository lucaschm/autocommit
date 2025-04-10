# 3rd party imports
import yaml

# built-in imports
import sys
from pathlib import Path

# project imports
from logger import get_logger

logger = get_logger()

class Config:
    _instance = None

    def __init__(self, config_file="config.yaml"):
        if Config._instance is not None:
            raise RuntimeError("Use Config.get_instance() to access the config instance.")

        logger.info("Loading configuration...")
        try:
            with open(config_file, "r") as f:
                self._data = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file '{config_file}' not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing '{config_file}': {e}")
            sys.exit(1)

        Config._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance

    def get(self, key, default=None):
        return self._data.get(key, default)

    @property
    def repo_path(self):
        return self.get("repo_path", "")

    @property
    def main_folders(self):
        return self.get("main_folders", [])

    @property
    def main_extensions(self):
        return self.get("main_extensions", [])

    @property
    def attachment_folders(self):
        return self.get("attachment_folders", [])

    @property
    def attachment_extensions(self):
        return self.get("attachment_extensions", [])

    @property
    def excluded_dirs(self):
        return set(self.get("excluded_dirs", []))

    def load_gitignore_patterns(self):
        gitignore_path = Path(self.repo_path) / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        return []
