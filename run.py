#!/var/www/pyenv/bin/python
# -*- coding:utf-8 -*-

import app

if __name__=='__main__':
	app.application.run(host='0.0.0.0',port=8400,debug=True)
