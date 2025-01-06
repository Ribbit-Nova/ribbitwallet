from contextvars import ContextVar
import logging
import json
import uuid
import os

trace_id_var: ContextVar[str] = ContextVar("trace_id", default=str(uuid.uuid4()))

# Add a filter to include trace_id in logs
class TraceIDFilter(logging.Filter):
    def filter(self, record):
        record.traceid = trace_id_var.get()
        return True

# Mask sensitive information in logs
class MaskingFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            record.msg = self.mask_sensitive_info(record.msg)
        if hasattr(record, 'args'):
            record.args = tuple(self.mask_sensitive_info(arg) for arg in record.args)
        return True

    def mask_sensitive_info(self, msg):
        # Example masking logic, you can customize it as needed
        if isinstance(msg, str):
            msg = self.mask_param_values(msg)
        return msg

    def mask_param_values(self, msg):
        # Example masking logic for parameter values
        sensitive_params = os.getenv("LOGS_MASKING_PARAMS").split(",")
        for param in sensitive_params:
            if param in msg:
                try:
                    start_index = msg.index(f"'{param}': '") + len(f"'{param}': '")
                    end_index = msg.index("'", start_index)
                    value = msg[start_index:end_index]
                    msg = msg.replace(value, "******")
                except ValueError:
                    continue
        return msg

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "traceid": getattr(record, 'traceid', ''),
            "name": record.name,
            "message": record.getMessage(),
            "object": getattr(record, 'object', '')
        }
        return json.dumps(log_record)