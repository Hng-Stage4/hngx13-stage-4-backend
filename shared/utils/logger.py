# shared/utils/logger.py
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service_name": record.__dict__.get("service_name", "unknown"),
            "correlation_id": record.__dict__.get("correlation_id", None),
            "event": record.__dict__.get("event", None),
            "message": record.getMessage(),
        }
        return json.dumps(log_record)

def get_logger(service_name: str):
    logger = logging.getLogger(service_name)
    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
