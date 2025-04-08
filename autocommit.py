# 3rd party imports
from watchdog.observers import Observer

# project imports
from autocommit.config import Config
from autocommit.note_handler import NoteHandler
from autocommit.logger import get_logger

def main():

    logger = get_logger()

    logger.info("Starting autocommit...")

    config = Config.get_instance()

    event_handler = NoteHandler()
    observer = Observer()
    observer.schedule(event_handler, path=config.repo_path, recursive=True)
    observer.start()

    logger.info("Observer started, waiting for events...")

    observer.join()

if __name__ == "__main__":
    main()
