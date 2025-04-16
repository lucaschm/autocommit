import signal
import sys
from watchdog.observers import Observer

from autocommit.logger import get_logger
from autocommit.git import commit_and_push

logger = get_logger()

class ExitHandler:
    _workspace = None
    _observer = None

    def __init__(self, workspace: str, observer: Observer):
        self._workspace = workspace
        self._observer = observer
        self.prepare_for_exit()

    def handle_exit(self, *args):
        logger.info("Exiting... Committing last edited files.")
        commit_and_push(self._workspace, '*', "save * (autocommit exit)")
        self._observer.stop()
        sys.exit(0)

    def prepare_for_exit(self):
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

