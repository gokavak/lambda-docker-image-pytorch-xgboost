import sys
import logging

def init_logger():
    '''
    Initialize a Logger that prints to the console following 
    the format %m/%d/%Y %I:%M:%S to indicate the event's datetime

    Returns
    -------
    logger: Logger
        A formatted logger.
    '''

    # Initialize Logger and set Level to INFO
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    return logger


def add_handler(logger):
    
    if not logger.hasHandlers():
    
        # Initialize a Handler to print to stdout
        handler = logging.StreamHandler(sys.stdout)
    
        # Format Handler output
        logFormatter = logging.Formatter(
            "%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
        )
        handler.setFormatter(logFormatter)
    
        # Set Handler Level to INFO
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    return logger