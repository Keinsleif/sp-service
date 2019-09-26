#!/var/www/venv/bin/python3
# -*- encode: utf-8 -*-

from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import mysql.connector


ws_list = set()

def chat_handle(environ, start_response):
	ws = environ['wsgi.websocket']
	ws_list.add(ws)

	print('enter:', len(ws_list), environ['REMOTE_ADDR'], environ['REMOTE_PORT'])

	while True:
		msg = ws.receive()
		if msg is None:
			break

		remove = set()
		for s in ws_list:
			try:
				s.send(msg)
			except Exception:
				remove.add(s)

		for s in remove:
			ws_list.remove(s)

		with open("/var/www/html/sp-service/static/chat/chat.txt",'r+') as f:
			d=f.read()
			f.seek(0)
			f.write(msg+"\n"+d)


	print('exit:', environ['REMOTE_ADDR'], environ['REMOTE_PORT'])
	ws_list.remove(ws)


def myapp(environ, start_response):
	path = environ['PATH_INFO']
	if path == '/chat':
		return chat_handle(environ, start_response)
	else:
		start_response('404 Not Found.', [('Content-Type', 'text/plain')])
		return 'not found'


if __name__ == '__main__':
	server = pywsgi.WSGIServer(('127.0.0.1', 9250), myapp, handler_class=WebSocketHandler)
	print("Starting Gevent Websocket Server.")
	server.serve_forever()
