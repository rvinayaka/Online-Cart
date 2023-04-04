import logging
import os

def logger(name):
    # Create logger instance
    logger = logging.getLogger(name)
    # stop propagating to root logger
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    # Setting path for the log files
    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep), 'Logs')
    # Setting file name for the log file
    log_fname = os.path.join(log_dir, 'cart.log')
    # Setting format for the log message
    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
    # creating file handler for the log file
    file_handler = logging.FileHandler(log_fname)
    # setting level for the handler
    file_handler.setLevel(logging.DEBUG)
    # setting format for the handler
    file_handler.setFormatter(formatter)
    # Adding handler to the logger.
    logger.addHandler(file_handler)
    # returning the instance of the logger.
    return logger