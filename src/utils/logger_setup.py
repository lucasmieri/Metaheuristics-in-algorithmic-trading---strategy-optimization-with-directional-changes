import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_format: str = "detailed",
    console_output: bool = True,
    file_output: bool = True,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers = []
    
    if log_format == "simple":
        formatter = logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        )
    else:  
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    if file_output:
        if log_dir is None:
            from config.paths import LOGS_DIR
            log_dir = LOGS_DIR
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{name}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger