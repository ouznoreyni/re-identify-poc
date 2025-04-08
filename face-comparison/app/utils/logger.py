# import logging
# from logging.handlers import RotatingFileHandler
# import os
# from datetime import datetime
# from app.core.config import settings
#
#
# class RequestIdFilter(logging.Filter):
#     def filter(self, record):
#         record.request_id = getattr(record, 'request_id', 'NO_REQUEST_ID')
#         return True
#
#
# def setup_logging():
#     """Configure comprehensive logging for the application"""
#     os.makedirs("logs", exist_ok=True)
#
#     logger = logging.getLogger("face_api")
#     logger.setLevel(logging.INFO)
#
#     formatter = logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
#
#     # Console handler with color
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)
#     #console_handler.addFilter(RequestIdFilter())
#
#     # File handler with rotation
#     file_handler = RotatingFileHandler(
#         f"logs/face_api_{datetime.now().strftime('%Y-%m-%d')}.log",
#         maxBytes=10 * 1024 * 1024,  # 10MB
#         backupCount=5,
#         encoding='utf-8'
#     )
#     file_handler.setFormatter(formatter)
#     #file_handler.addFilter(RequestIdFilter())
#
#     # Clear existing handlers
#     logger.handlers.clear()
#
#     logger.addHandler(console_handler)
#     logger.addHandler(file_handler)
#
#     # Configure uvicorn logging
#    # uvicorn_logger = logging.getLogger("uvicorn")
#    # uvicorn_logger.handlers.clear()
#     #uvicorn_logger.addHandler(console_handler)
#
#     #uvicorn_access = logging.getLogger("uvicorn.access")
#     #uvicorn_access.handlers.clear()
#     #uvicorn_access.addHandler(file_handler)
#
#     return logger
#
#
# logger = setup_logging()
