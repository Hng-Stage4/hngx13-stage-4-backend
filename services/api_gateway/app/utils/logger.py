"""
Logging Configuration
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """
    Setup application logging
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger