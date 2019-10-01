#!/var/www/venv/bin/python3
# -*- encode: utf-8 -*-

from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import json
import html
import logging
import re
import os

LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'INFO'

logger=logging.getLogger(__name__)
ws_list = set()
patt1=re.compile('/chat/(.*)')

def chat_handle(environ, start_response, room):
	ws = environ['wsgi.websocket']
	ws_list.add(ws)

	logger.info('enter:', len(ws_list), environ['REMOTE_ADDR'], environ['REMOTE_PORT'])

	while True:
		msg=ws.receive()
		if msg is None:
			break
		msg = json.loads(msg)
		if msg["message"] is None:
			break

		msg={"message": html.escape(msg["message"]),"writer": msg["writer"],"color": msg["color"],}

		remove = set()
		for s in ws_list:
			try:
				s.send(json.dumps(msg))
			except Exception:
				remove.add(s)

		for s in remove:
			ws_list.remove(s)

		with open("/var/www/html/sp-service/static/chat/"+room+".txt",'r+') as f:
			d=f.read()
			f.seek(0)
			f.write('<div class="alert alert-'+msg["color"]+'">'+msg["writer"]+': '+msg["message"]+"</div>\n"+d)


	logger.info('exit:', environ['REMOTE_ADDR'], environ['REMOTE_PORT'])
	ws_list.remove(ws)


def myapp(environ, start_response):
	path = environ['PATH_INFO']
	logger.info('start:'+path)
	if path == '/chat':
		return chat_handle(environ, start_response,room="chat")
	d=patt1.findall(path)
	logger.info('d='+d[0])
	if 	os.path.exists('/var/www/html/sp-service/static/chat/'+d[0]+'.txt'):
		return chat_handle(environ, start_response,room=d[0])
	else:
		start_response('404 Not Found.', [('Content-Type', 'text/plain')])
		return 'not found'


if __name__ == '__main__':
	server = pywsgi.WSGIServer(('127.0.0.1', 9250), myapp, handler_class=WebSocketHandler)
	logger.info("Starting Gevent Websocket Server.")
	server.serve_forever()
