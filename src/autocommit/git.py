# built-in imports
import subprocess
import os
import time

# project imports
from autocommit.logger import get_logger

logger = get_logger()

# TODO: improve code quality in try methods. while retries > 0 and if retries == 0 is not clean

def try_add(workspace: str, filepath: str) -> bool:
    retries = 3
    while retries > 0:
        try:
            logger.info(f'git -C "{workspace}" add "{filepath}"')
            subprocess.run(['git', '-C', workspace, 'add', filepath], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to add {filepath}: {e}, retrying...")
            retries -= 1
            time.sleep(1)
    if retries == 0:
        logger.error(f"Failed to add {filepath} after multiple attempts.")
        raise RuntimeError(f"Failed to add {filepath} after multiple attempts")


def try_commit(workspace: str, commit_message: str) -> bool:
    # Attempt to commit changes with retries
    commit_retries = 3
    while commit_retries > 0:
        try:
            logger.info(f'git -C "{workspace}" commit -m "{commit_message}"')
            commit_result = subprocess.run(['git', '-C', workspace, 'commit', '-m', commit_message], check=True, text=True, stdout=subprocess.PIPE)
            logger.info(f"git output: \n{commit_result.stdout}")
            return True  # Exit the loop if commit is successful
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to commit {commit_message}: {e}, retrying...")
            commit_retries -= 1
            time.sleep(1)
    if commit_retries == 0:
        logger.error(f"Failed to commit {commit_message} after multiple attempts.")
        return False # commit failed

def try_push(workspace: str) -> None:
    # Attempt to push changes with retries
    push_retries = 3
    while push_retries > 0:
        try:
            logger.info(f'git -C "{workspace}" push')
            push_result = subprocess.run(
                ['git', '-C', workspace, 'push'],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT  # Merge stderr into stdout
            )
            logger.info(f"git output: \n{push_result.stdout}")
            return True  # Exit the loop if push is successful
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to push: {e}, retrying...")
            push_retries -= 1
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Possible network issue while pushing: {e}")
            push_retries -= 1
            time.sleep(1)
    if push_retries == 0:
        logger.warning(f"Failed to push after multiple attempts. Check your network connection.")
        return False # push failed

# return true if pull was successful. false otherwise
def try_pull(workspace: str) -> bool:
    # Attempt to push changes with retries
    pull_retries = 3
    while pull_retries > 0:
        try:
            logger.info(f'git -C "{workspace}" pull')
            pull_result = subprocess.run(['git', '-C', workspace, 'pull'], check=True, text=True, stdout=subprocess.PIPE)
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

def commit_and_push(workspace: str, filepath: str, commit_message: str) -> None:
    try:
        try_add(workspace, filepath)
        try_commit(workspace, commit_message)
        try_push(workspace)
    except RuntimeError:
        logger.warning("Cancel commit_and_push().")


def git_rm(workspace: str, path: str) -> bool:
    retries = 3
    while retries > 0:
        try:
            logger.info(f'git -C "{workspace}" rm -r "{path}"')
            rm_result = subprocess.run(['git', '-C', workspace, 'rm', '-r', path], check=True, text=True, stdout=subprocess.PIPE)
            logger.info(f"git output: \n{rm_result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to remove {path}: {e}, retrying...")
            retries -= 1
            time.sleep(1)
    if retries == 0:
        logger.error(f"Failed to remove {path} after multiple attempts")
        raise RuntimeError(f"Failed to remove {path} after multiple attempts")

def delete_directory(workspace: str, path: str, commit_message: str) -> None:
    try:
        logger.info(f"delete_directory({path}, {commit_message})")
        rm_result = subprocess.run(['git', '-C', workspace, 'rm', '-r', path], check=True, text=True, stdout=subprocess.PIPE)
        logger.info(f"git output: \n{rm_result.stdout}")
        diff_result = subprocess.run(['git', '-C', workspace, 'diff', '--cached', '--exit-code'], capture_output=True)
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

# returns the root of the git repo of "path". 
# "path" must be part of a git repo.
def get_repo_root(path: str) -> str:
    if (os.path.isfile(path)):
        dirname, basename = os.path.split(path)
    elif (os.path.isdir(path)):
        dirname = path
    else:
        raise ValueError("path must refer to a valid file or directory!")
    result = subprocess.run(['git', '-C', dirname, 'rev-parse', '--show-toplevel'], capture_output=True)
    if ("not a git repository" in str(result.stderr)):
        raise ValueError(f"'{path}' is not part of a git repository!")
    if (result.returncode != 0): # if something went wrong
        raise RuntimeError(f"Something went wrong while determining repo root of '{path}'")
    
    git_root = result.stdout.decode('utf-8').strip()
    return git_root