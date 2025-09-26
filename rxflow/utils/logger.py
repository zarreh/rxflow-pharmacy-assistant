"""
Logging setup for RxFlow Pharmacy Assistant
"""

import logging
import sys
from typing import Optional
from rxflow.config.settings import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup application logging configuration"""
    settings = get_settings()
    level = log_level or settings.log_level
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root logger configuration
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[console_handler],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name"""
    return logging.getLogger(name)