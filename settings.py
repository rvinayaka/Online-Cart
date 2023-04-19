import logging
import os

import psycopg2
from flask import jsonify

def connection():
    cur, conn = None, None
    try:
        conn = psycopg2.connect(
            host="172.16.1.236",
            port="5432",
            database="bctst",
            user="vinayak",
            password="vinayak"
        )
        cur = conn.cursor()
        print("DB connected")
        print(cur, conn)
        return cur, conn
    except(Exception, psycopg2.Error) as error:
        print("Failed connection", error)
        return cur, conn


def logger(name):
    # Create logger instance
    logger = logging.getLogger(name)
    if not any(isinstance(handler, logging.FileHandler) for handler in logging.getLogger(name).handlers):
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

# def logger(name):
#     # Check if the logger already has a file handler
#     if not any(isinstance(handler, logging.FileHandler) for handler in logging.getLogger(name).handlers):
#         # Create logger instance
#         logger = logging.getLogger(name)
#         # stop propagating to root logger
#         logger.propagate = False
#         logger.setLevel(logging.DEBUG)
#         # Setting path for the log files
#         log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep), 'Logs')
#         # Setting file name for the log file
#         log_fname = os.path.join(log_dir, 'cart.log')
#         # Setting format for the log message
#         formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
#         # creating file handler for the log file
#         file_handler = logging.FileHandler(log_fname)
#         # setting level for the handler
#         file_handler.setLevel(logging.DEBUG)
#         # setting format for the handler
#         file_handler.setFormatter(formatter)
#         # Adding handler to the logger.
#         logger.addHandler(file_handler)
#     # returning the instance of the logger.
#     return logger



def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as error:
            conn = kwargs.get('conn')
            if conn:
                conn.rollback()
            logger(__name__).error(f"Error occurred 1: {error}")
            return jsonify({"message": f"Error occurred: {error}"})
        except Exception as error:
            logger(__name__).error(f"Error occurred 2: {error}")
            return jsonify({"message": f"Error occurred: {error}"})
        finally:
            conn = kwargs.get("conn")
            cur = kwargs.get("cur")
            # close the database connection
            if conn:
                conn.close()
            if cur:
                cur.close()
    return wrapper
