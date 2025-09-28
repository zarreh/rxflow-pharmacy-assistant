"""
Logging setup for RxFlow Pharmacy Assistant
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from rxflow.config.settings import get_settings

# Global registry of session-specific loggers
_session_loggers: Dict[str, logging.Logger] = {}

def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup application logging configuration"""
    settings = get_settings()
    level = log_level or settings.log_level

    # Configure logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger configuration
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[console_handler],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def _ensure_logs_directory() -> Path:
    """Ensure logs directory exists and return path"""
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name"""
    return logging.getLogger(name)


def get_session_logger(session_id: str, logger_name: str = "conversation") -> logging.Logger:
    """Get or create a session-specific logger that writes to both console and file"""
    
    # Check if we already have a logger for this session
    logger_key = f"{session_id}_{logger_name}"
    if logger_key in _session_loggers:
        return _session_loggers[logger_key]
    
    # Create new session logger
    session_logger = logging.getLogger(f"rxflow.session.{session_id[:8]}")
    session_logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times
    if session_logger.handlers:
        _session_loggers[logger_key] = session_logger
        return session_logger
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler (same as before)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    session_logger.addHandler(console_handler)
    
    # File handler for this session
    logs_dir = _ensure_logs_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"conversation_{session_id[:8]}_{timestamp}.log"
    log_filepath = logs_dir / log_filename
    
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setFormatter(formatter)
    session_logger.addHandler(file_handler)
    
    # Add session info header to the log file
    session_logger.info(f"=" * 80)
    session_logger.info(f"NEW CONVERSATION SESSION STARTED")
    session_logger.info(f"Session ID: {session_id}")
    session_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    session_logger.info(f"Log File: {log_filename}")
    session_logger.info(f"=" * 80)
    
    # Store in registry
    _session_loggers[logger_key] = session_logger
    
    return session_logger


def close_session_logger(session_id: str) -> None:
    """Close and cleanup session logger"""
    logger_key = f"{session_id}_conversation"
    if logger_key in _session_loggers:
        session_logger = _session_loggers[logger_key]
        
        # Log session end
        session_logger.info(f"=" * 80)
        session_logger.info(f"CONVERSATION SESSION ENDED")
        session_logger.info(f"Session ID: {session_id}")
        session_logger.info(f"End Timestamp: {datetime.now().isoformat()}")
        session_logger.info(f"=" * 80)
        
        # Close file handlers
        for handler in session_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                session_logger.removeHandler(handler)
        
        # Remove from registry
        del _session_loggers[logger_key]


def get_all_session_logs() -> Dict[str, Path]:
    """Get all available session log files"""
    logs_dir = _ensure_logs_directory()
    log_files = {}
    
    for log_file in logs_dir.glob("conversation_*.log"):
        # Extract session ID from filename
        parts = log_file.stem.split('_')
        if len(parts) >= 2:
            session_id = parts[1]
            log_files[session_id] = log_file
    
    return log_files
