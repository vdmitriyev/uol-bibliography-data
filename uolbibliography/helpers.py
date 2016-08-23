import os
import socket
import logging

def custom_logger(path_to_log_file=None, logger_name=None):
    """ Configuring logger and setting proper path to file.

    Args:
        path_to_log_file: name of the log file in subfolder 'logs', in case None will be generated

    Returns:
        logger that is able to write to files and console at once
    """

    if not logger_name:
        logger_name = 'root'

    print (logger_name)

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger(logger_name)
    rootLogger.setLevel(logging.DEBUG)

    if path_to_log_file is None:
        logs_folder = 'logs'
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
        path_to_log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), logs_folder, '{0}-{1}'.format(socket.gethostname(), 'root'))
        #print ('[i] will be logged in to {0}'.format(path_to_log_file))

    # # take care, here is a magic string!!! configure this for own needs
    fileHandler = logging.FileHandler("{path}.log".format(path=path_to_log_file))
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)
    rootLogger.addHandler(consoleHandler)
    #rootLogger.info('\n')

    return rootLogger
