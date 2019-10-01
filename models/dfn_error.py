#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

from flask import request, g, current_app, logging, render_template
import traceback
from http import HTTPStatus
import yaml

with open("sp-service/config/env.conf","r") as f:
        data=yaml.load(f)
for i in data:
        exec(i+"='"+data[i]+"'")

def exception_handler(ex):
	logger=logging.create_logger(current_app)

	logger.error(traceback.format_exc())
	if MODE=='DEBUG':
		return (render_template("error.html",error=traceback.format_exc()),HTTPStatus.INTERNAL_SERVER_ERROR)
	else:
		return (render_template("error.html"),HTTPStatus.INTERNAL_SERVER_ERROR)

def not_found_handler(ex):
	logger=logging.create_logger(current_app)

	logger.info('Not Found '+request.url)

	return (render_template("404.html"),HTTPStatus.NOT_FOUND)

def over_max_file_size_handler(error):
	logger=logging.create_logger(current_app)

	logger.info('file size is overed. '+request.url)

	return(render_template("size_over.html",title="File Size is Over!"))
