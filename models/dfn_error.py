#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

from flask import request, g, current_app, logging, render_template
import traceback
from http import HTTPStatus
import yaml

with open("config/env.conf","r") as f:
        data=yaml.safe_load(f)
for i in data:
        exec(i+"='"+str(data[i])+"'")

def exception_handler(ex):
	logger=logging.create_logger(current_app)

	logger.error(traceback.format_exc())
	if MODE=='DEBUG':
		return (render_template("error.html",error=traceback.format_exc()),HTTPStatus.INTERNAL_SERVER_ERROR)
	else:
		return (render_template("error.html"),HTTPStatus.INTERNAL_SERVER_ERROR)

def not_found_handler(ex):
	logger=logging.create_logger(current_app)

	logger.error('Not Found '+request.url)

	return (render_template("404.html"),HTTPStatus.NOT_FOUND)

def over_max_file_size_handler(error):
	logger=logging.create_logger(current_app)

	logger.error('file size is overed. '+request.url)

	return(render_template("size_over.html",title="File Size is Over!"))

def init_app(app,log_dir='/var/log/sp-service'):
	import logging
	from logging.handlers import RotatingFileHandler
	formatter=logging.Formatter(
		'[%(asctime)s] requested %(url)s \n'
		'%(levelname)s in %(module)s: %(message)s'
	)
	debug_log = '/var/log/sp-service/main.log'
	debug_file_handler = RotatingFileHandler(
		debug_log, maxBytes=100000, backupCount=10
	)

	debug_file_handler.setLevel(logging.INFO)
	debug_file_handler.setFormatter(formatter)
	app.logger.addHandler(debug_file_handler)

	error_log = '/var/log/sp-service/error.log'
	error_file_handler = RotatingFileHandler(
		error_log, maxBytes=100000, backupCount=10
	)
	error_file_handler.setLevel(logging.ERROR)
	error_file_handler.setFormatter(formatter)
	app.logger.addHandler(error_file_handler)

	app.logger.setLevel(logging.DEBUG)
