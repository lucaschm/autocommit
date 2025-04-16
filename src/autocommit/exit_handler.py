import signal
import sys
from watchdog.observers import Observer
import psutil
import threading

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
        self.monitor_obsidian_exit(self.on_obsidian_exit)

    def handle_exit(self, *args):
        logger.info("Exiting... Committing last edited files.")
        commit_and_push(self._workspace, '*', "save * (autocommit exit)")
        self._observer.stop()
        sys.exit(0)

    def prepare_for_exit(self):
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def on_obsidian_exit(self):
        logger.info("Obsidian has exited! Committing last edited files.")
        commit_and_push(self._workspace, '*', "save * (autocommit exit)")

    def monitor_obsidian_exit(self, callback):
        # Find the first Obsidian process
        for proc in psutil.process_iter(['pid', 'name']):
            if 'obsidian' in proc.info['name'].lower():
                threading.Thread(target=self.wait_and_trigger, args=(proc.pid, callback), daemon=True).start()
                logger.info(f"Monitoring Obsidian (PID: {proc.pid}) for exit.")
                return
        logger.warning("Obsidian is not currently running.")

    def wait_and_trigger(self, pid, callback):
        try:
            proc = psutil.Process(pid)
            proc.wait()  # This blocks until the process exits
            callback()
        except psutil.NoSuchProcess:
            logger.info("Obsidian process already exited.")
