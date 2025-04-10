# 3rd party imports
from watchdog.observers import Observer

# project imports
from autocommit.config import Config
from autocommit.note_handler import NoteHandler
from autocommit.logger import get_logger
from autocommit.git import is_git_repo

def main():

    logger = get_logger()

    config = Config.get_instance()

    if (not is_git_repo(config.repo_path)):
        logger.error(f"{config.repo_path} is not a git repository!")
        return

    logger.info("Starting autocommit...")

    event_handler = NoteHandler()
    observer = Observer()
    observer.schedule(event_handler, path=config.repo_path, recursive=True)
    observer.start()

    logger.info("Observer started, waiting for events...")

    observer.join()

if __name__ == "__main__":
    main()
