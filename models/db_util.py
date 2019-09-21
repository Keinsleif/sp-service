#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

import mysql.connector
from flask import current_app, g

def get_db():
	if not hasattr(g, 'db'):
		g.db=mysql.connector.connect(host='localhost',user='python',password='sp-no8',database='spservice_dev')
	return g.db


def close_db(error):
	if hasattr(g, 'db'):
		g.db.close()

def init_app(app):
	app.teardown_appcontext(close_db)
