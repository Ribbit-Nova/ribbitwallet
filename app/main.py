from fastapi import FastAPI, Request # type: ignore
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from app.router import router
from configs.logging_fitlers import MaskingFilter, TraceIDFilter, JSONFormatter
import os
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
app.include_router(router)

# Configure logging
log_folder = os.getenv('LOG_FOLDER')
log_file_name = os.getenv('LOG_FILE_NAME')

if not log_folder or not log_file_name:
    raise ValueError('LOG_FOLDER and LOG_FILE_NAME environment variables must be set')

# Ensure the logs directory exists
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Define the custom JSON formatter
json_formatter = JSONFormatter()
log_handler = TimedRotatingFileHandler(os.path.join(log_folder, log_file_name), when='midnight', interval=1, backupCount=30)
log_handler.setFormatter(json_formatter)
log_handler.setLevel(logging.INFO)

# Rename the log file to include the date
log_handler.namer = lambda name: name.replace(log_file_name, f"{log_file_name.split('.')[0]}-{datetime.now().strftime('%Y-%m-%d')}.log")

app_logger = logging.getLogger()
log_level = os.getenv('LOG_LEVEL').upper()
app_logger.setLevel(getattr(logging, log_level))
app_logger.addHandler(log_handler)

trace_id_filter = TraceIDFilter()
app_logger.addFilter(trace_id_filter)

masking_filter = MaskingFilter()
app_logger.addFilter(masking_filter)