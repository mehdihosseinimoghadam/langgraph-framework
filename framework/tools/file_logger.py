import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def log_output(context: Dict[str, Any], log_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Log the output to a file.

    Args:
        context: The current context
        log_dir: Directory to save logs (defaults to 'logs' in current directory)

    Returns:
        Dictionary with log status and path
    """
    try:
        # Create log directory if it doesn't exist
        log_dir = log_dir or os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Create a timestamp for the log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"log_{timestamp}.json")

        # Extract relevant data from context
        log_data = {
            "timestamp": timestamp,
            "data": context
        }

        # Write to file
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)

        logger.info(f"Logged output to {log_file}")

        return {
            "status": "success",
            "log_file": log_file
        }

    except Exception as e:
        logger.error(f"Error logging output: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
