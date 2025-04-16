import signal
import sys
from watchdog.observers import Observer
import psutil
import threading
import time

from autocommit.logger import get_logger
from autocommit.git import commit_and_push

logger = get_logger()

class ExitHandler:
    def __init__(self, workspace: str, observer: Observer):
        self._workspace = workspace
        self._observer = observer
        self._obsidian_is_monitored = False
        self._lock = threading.Lock()

        self.prepare_for_exit()
        self.start_obsidian_monitor_loop()

    def handle_exit(self, *args):
        logger.info("Exiting... Committing last edited files.")
        commit_and_push(self._workspace, '*', "save * (autocommit exit)")
        self._observer.stop()
        sys.exit(0)

    def prepare_for_exit(self):
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def on_obsidian_exit(self, pid):
        logger.info(f"Obsidian process (PID {pid}) exited. Committing last edited files.")
        commit_and_push(self._workspace, '*', f"save * (autocommit)")
        with self._lock:
            self._obsidian_is_monitored = False

    def start_obsidian_monitor_loop(self):
        thread = threading.Thread(target=self._obsidian_monitor_loop, daemon=True)
        thread.start()

    def _obsidian_monitor_loop(self):
        logger.info("Starting Obsidian monitor loop.")
        while True:
            for proc in psutil.process_iter(['pid', 'name']):
                if 'obsidian' in proc.info['name'].lower():
                    pid = proc.info['pid']
                    with self._lock:
                        if not self._obsidian_is_monitored:
                            self._obsidian_is_monitored = True
                            threading.Thread(target=self._wait_for_exit, args=(pid,), daemon=True).start()
                            logger.info(f"Monitoring Obsidian (PID {pid}) for exit.")
                            break # one monitored obsidian process is enough
            time.sleep(5)

    def _wait_for_exit(self, pid):
        try:
            psutil.Process(pid).wait()
            self.on_obsidian_exit(pid)
        except psutil.NoSuchProcess:
            logger.info(f"Obsidian process (PID {pid}) already exited.")
            with self._lock:
                self._obsidian_is_monitored = False
