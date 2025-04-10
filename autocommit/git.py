# built-in imports
import subprocess
import time

# project imports
from autocommit.logger import get_logger
from autocommit.config import Config

logger = get_logger()
config = Config.get_instance()

def try_add(filename: str) -> None:
    retries = 3
    while retries > 0:
        try:
            logger.info(f"git add: {filename}")
            subprocess.run(['git', '-C', config.repo_path, 'add', filename], check=True)
            break
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to add {filename}: {e}, retrying...")
            retries -= 1
            time.sleep(1)
    if retries == 0:
        raise Exception(f"Failed to add {filename} after multiple attempts")

def try_commit(filename: str, commit_message: str) -> None:
    # Attempt to commit changes with retries
    commit_retries = 3
    while commit_retries > 0:
        try:
            logger.info(f"git commit: {commit_message}")
            commit_result = subprocess.run(['git', '-C', config.repo_path, 'commit', '-m', commit_message], check=True, text=True, stdout=subprocess.PIPE)
            logger.info(f"git output: \n{commit_result.stdout}")
            break  # Exit the loop if commit is successful
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to commit {commit_message}: {e}, retrying...")
            commit_retries -= 1
            time.sleep(1)
    if commit_retries == 0:
        logger.error(f"Failed to commit {commit_message} after multiple attempts")
        return

def try_push(filename: str) -> None:
    # Attempt to push changes with retries
    push_retries = 3
    while push_retries > 0:
        try:
            logger.info(f"git push: {commit_message}")
            push_result = subprocess.run(['git', '-C', config.repo_path, 'push'], check=True, text=True, stdout=subprocess.PIPE)
            logger.info(f"git output: \n{push_result.stdout}")
            break  # Exit the loop if push is successful
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to push {commit_message}: {e}, retrying...")
            push_retries -= 1
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Possible network issue while pushing {commit_message}: {e}")
            push_retries -= 1
            time.sleep(1)
    if push_retries == 0:
        logger.warning(f"Failed to push {commit_message} after multiple attempts. Check your network connection.")

# return true if pull was successful. false otherwise
def try_pull() -> bool:
    # Attempt to push changes with retries
    pull_retries = 3
    while pull_retries > 0:
        try:
            logger.info(f"git pull")
            pull_result = subprocess.run(['git', '-C', config.repo_path, 'pull'], check=True, text=True, stdout=subprocess.PIPE)
            logger.info(f"git output: \n{pull_result.stdout}")
            return True  # Exit if pull is successful
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to pull: {e}, retrying...")
            pull_retries -= 1
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Possible network issue while pulling: {e}")
            pull_retries -= 1
            time.sleep(1)
    if pull_retries == 0:
        logger.warning(f"Failed to pull after multiple attempts. Check your network connection.")
        return False # pull failed

def commit_and_push(filename: str, commit_message: str) -> None:
    try_add(filename)
    try_commit(filename, commit_message)
    try_push(filename)


def git_rm(path: str) -> None:
    retries = 3
    while retries > 0:
        try:
            logger.info(f"git rm -r: {path}")
            rm_result = subprocess.run(['git', '-C', config.repo_path, 'rm', '-r', path], check=True, text=True, stdout=subprocess.PIPE)
            logger.info(f"git output: \n{rm_result.stdout}")
            break
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to remove {path}: {e}, retrying...")
            retries -= 1
            time.sleep(1)
    if retries == 0:
        raise Exception(f"Failed to remove {path} after multiple attempts")

def delete_directory(path: str, commit_message: str) -> None:
    logger.info(f"delete_directory({path}, {commit_message})")
    try:
        rm_result = subprocess.run(['git', '-C', config.repo_path, 'rm', '-r', path], check=True, text=True, stdout=subprocess.PIPE)
        logger.info(f"git output: \n{rm_result.stdout}")
        diff_result = subprocess.run(['git', '-C', config.repo_path, 'diff', '--cached', '--exit-code'], capture_output=True)
        if diff_result.returncode == 1:  # There are changes to commit
            git_commit_and_push(path, commit_message)
            logger.info(f"Deleted directory: {path} with message: {commit_message}")
        else:
            logger.info(f"No changes to commit for: {path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error committing deletion of {path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# This method returns true, if path is a git repo.
# Otherwise it returns false.
def is_git_repo(path: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        message = "Git is not installed on this system"
        logger.error(message)
        raise RuntimeError(message)
