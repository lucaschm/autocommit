# 3rd party imports
from watchdog.observers import Observer

# project imports
from autocommit.config import Config
from autocommit.note_handler import NoteHandler
from autocommit.logger import get_logger
from autocommit.git import is_git_repo, try_pull
from autocommit.exit_handler import ExitHandler

def main():

    logger = get_logger()

    config = Config.get_instance()
    
    logger.info("Starting autocommit...")

    if (not is_git_repo(config.repo_path)):
        logger.error(f"{config.repo_path} is not a git repository! \
        Change repo_path in .../autocommit/config.yaml")
        return

    if (not try_pull(config.repo_path)): # if git pull fails
        proceed = input("WARNING! Unable to pull from remote. Do you want to proceed without pulling? This could result in git conflicts! (y/n): ").strip().lower()
        if proceed != 'y':
            logging.info("Exit because 'git pull' didn't work.")
            exit(1)
        else:
            logging.warning("Starting script without 'git pull'.")

    event_handler = NoteHandler(config.repo_path)
    observer = Observer()
    observer.schedule(event_handler, path=config.repo_path, recursive=True)
    observer.start()

    ExitHandler(config.repo_path, observer)

    logger.info("Observer started, waiting for events...")

    observer.join()

if __name__ == "__main__":
    main()
