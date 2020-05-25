#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

import mysql.connector
from flask import current_app, g
import yaml

with open("config/env.conf","r") as f:
	data=yaml.safe_load(f)
for i in data:
	exec(i+"='"+str(data[i])+"'")

if MODE=="DEBUG":
	DB_NAME="spservice_dev"
elif MODE=="RELEASE":
	DB_NAME="spservice"

def get_db():
	if not hasattr(g, 'db'):
		g.db=mysql.connector.connect(host=DB_HOST,user=DB_USER,password=DB_USER_PASS,database=DB_NAME)
	return g.db


def close_db(error):
	if hasattr(g, 'db'):
		g.db.close()

def init_app(app):
	app.teardown_appcontext(close_db)
