# 3rd party imports
from watchdog.events import FileSystemEventHandler

# built-in imports
import os
import time
import subprocess # TODO: this can be removed when TODO 01 was solved

# project imports
from autocommit.util import file_exists, ignore_path, is_attachment_file, is_main_file
from autocommit.logger import get_logger
from autocommit.git import commit_and_push, delete_directory, git_rm

logger = get_logger()

class NoteHandler(FileSystemEventHandler):
    _last_edited_file = None
    _time_since_last_edit = None
    _workspace = None

    def __init__(self, workspace):
        self._workspace = workspace

    def dispatch(self, event):
        if ignore_path(event.src_path):
            #logger.debug(f"{event.src_path} is part of an excluded dir and will be ignored.")
            return  # Ignore .git and venv files
        super().dispatch(event)

    def on_modified(self, event):
        if event.is_directory:
            return
        filename = event.src_path
        file_path = os.path.relpath(filename, self._workspace)
        logger.info(f"{file_path} was modified")
        
        if is_attachment_file(file_path):
            commit_and_push(self._workspace, filename, f"add {filename} (autocommit)")
        elif is_main_file(file_path):
            if self._last_edited_file and self._last_edited_file != file_path:
                commit_and_push(self._workspace, self._last_edited_file, f"edit {self._last_edited_file} (autocommit)")
            self._last_edited_file = file_path
            self._time_since_last_edit = time.time()

    def on_created(self, event):
        if event.is_directory:
            logger.info(f"Some directory was created. This will be ignored.")
            return
        filename = event.src_path
        file_path = os.path.relpath(filename, self._workspace)
        logger.info(f"{file_path} was created")
        if is_attachment_file(file_path):
            commit_and_push(self._workspace, filename, f"create {filename} (autocommit)")

    # TODO: weird behavior when an untracked main file gets deleted
    def on_deleted(self, event):
        if event.is_directory:
            delete_directory(_workspace, event.src_path, f"delete directory {os.path.basename(event.src_path)}")
        
        filename = event.src_path
        file_path = os.path.relpath(filename, self._workspace)
        logger.info(f"{file_path} was deleted")
        
        if is_attachment_file(file_path):
            commit_and_push(self._workspace, filename, f"delete {file_path} (autocommit)")
        elif is_main_file(file_path):
            commit_and_push(self._workspace, filename, f"delete {file_path} (autocommit)")
            if self._last_edited_file and self._last_edited_file == file_path:
                self._last_edited_file = None
                self._time_since_last_edit = None

    def on_moved(self, event):
        try:

            if event.is_directory:
                logger.info(f"Some directory was moved. This will be ignored.")
                return

            # Commit the addition of the new path
            filename = event.dest_path
            file_path = os.path.relpath(filename, self._workspace)
            logger.info(f"{file_path} was moved (or renamed)")

            if is_attachment_file(file_path):
                git_rm(_workspace, event.src_path) # stage the deletion of the old path
                commit_and_push(self._workspace, filename, f"rename {event.src_path} to {event.dest_path} (autocommit)")
            elif is_main_file(file_path):
                if self._last_edited_file and self._last_edited_file != file_path and file_exists(self._last_edited_file):
                    commit_and_push(self._workspace, self._last_edited_file, f"edit {self._last_edited_file} (autocommit)")
                git_rm(_workspace, event.src_path) # stage the deletion of the old path
                self._last_edited_file = file_path
                self._time_since_last_edit = time.time()
        except subprocess.CalledProcessError as e: # TODO 01: This exception must be caught in the method where it occurs
            logger.error(f"Error committing move: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    
    # def on_opened(self, event):
    #     logger.info(f"opened {event.src_path}")

    # def on_closed(self, event):
    #     logger.info(f"closed {event.src_path}")
