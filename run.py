#!/var/www/venv/bin/python
# -*- coding:utf-8 -*-

import app

if __name__=='__main__':
	app.application.run(host='localhost',port=8400,debug=True)
