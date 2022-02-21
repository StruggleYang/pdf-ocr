#!/usr/bin/env python
# coding:utf-8
import logging.handlers
import os

DATE_FORMAT = "%m-%d-%Y %H:%M:%S.%p"
logging.basicConfig(datefmt=DATE_FORMAT)

logger = logging.getLogger('insurance.analysis')
logger.setLevel(logging.DEBUG)
user_path = os.path.expanduser('~')
rf_handler = logging.handlers.TimedRotatingFileHandler(
    '%s/insurance-analysis-all.log' % (user_path), when='midnight', interval=1, backupCount=7)
rf_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"))

f_handler = logging.FileHandler(
    '%s/insurance-analysis-error.log' % (user_path))
f_handler.setLevel(logging.ERROR)
f_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

logger.addHandler(rf_handler)
logger.addHandler(f_handler)
