import logging
import pathlib
from pathlib import Path
import os 

cwd = Path.cwd()

def setup_logger(
        logger_name: str,
        log_file: str,
        log_level: int = logging.INFO
) -> logging.Logger:
    """
    This function allows the system to create and write log data
    of the system's operations.

    Args:
        logger_name (str): the name of the log file to create
        log_file (str): file path to the log file
        log_level (int): the value of the log type (warn, info, debug)
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    format = logging.Formatter('%(asctime)s - %(name)s- %(levelname)s - %(message)s')
    file_handler.setFormatter(format)
    logger.addHandler(file_handler)

    return logger


def create_folder_and_log_file(
        folder_name:str,
        file_name:str
) -> pathlib.Path:
    
    new_path = cwd.joinpath(folder_name)

    # create folder_path only once if not exist
    new_path.mkdir(exist_ok=True)
    log_file_path = new_path.joinpath(file_name)

    # create file if not exist
    log_file_path.touch()

folder_name = "logs"

log_files_to_create = [
    "doc_handler.log",
    "voice_handler.log",
    "embedding_vec.log",
    "fastapi_app.log"]

for log_file in log_files_to_create:
    create_folder_and_log_file(folder_name, log_file)


# Set up the loggers for each file
doc_handler_logger = setup_logger("doc_handler", os.path.join(folder_name, "doc_handler.log"))
voice_handler_logger = setup_logger("voice_handler", os.path.join(folder_name, "voice_handler.log"))
fastapi_app_logger = setup_logger("fastapi_app", os.path.join(folder_name, "fastapi_app.log"))
embedding_vec_logger = setup_logger("embedding_vec", os.path.join(folder_name, "embedding_vec.log"))