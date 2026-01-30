import logging
import os
from datetime import datetime

def setup_logger():
    """Setup application logger with file and console handlers"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("customer_support")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with date-based rotation
    log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logger()
