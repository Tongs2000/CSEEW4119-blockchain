import logging
import os
import sys
from datetime import datetime

# Log format includes port for each record
LOG_FORMAT = '%(asctime)s - %(name)s[%(port)s] - %(levelname)s - %(message)s'

class PortFilter(logging.Filter):
    def __init__(self, port):
        super().__init__()
        self.port = str(port) if port is not None else 'N/A'

    def filter(self, record):
        record.port = self.port
        return True


def setup_logger(name, log_dir='logs', port=None, level=logging.INFO):
    """
    Create and configure a logger that writes to a timestamped file (including port)
    and to console, tagging each message with the port.

    Args:
        name (str): Logger name (classification by component)
        log_dir (str): Directory to store log files
        port (int): Port number to include in messages and filename
        level (int): Logging level (e.g. logging.DEBUG)
    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Build filename: name_port_timestamp.log
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    port_str = str(port) if port is not None else 'NA'
    filename = f"{name}_{port_str}_{ts}.log"
    filepath = os.path.join(log_dir, filename)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Remove existing handlers to prevent duplicates
    logger.handlers.clear()

    # Create handlers
    file_handler = logging.FileHandler(filepath)
    console_handler = logging.StreamHandler(sys.stdout)

    # Formatter with port placeholder
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Attach filter to inject port into records
    port_filter = PortFilter(port)
    logger.addFilter(port_filter)
    file_handler.addFilter(port_filter)
    console_handler.addFilter(port_filter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Print log file location
    print(f"Log file created at: {filepath}")
    
    return logger
