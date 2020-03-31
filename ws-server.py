#!/var/www/venv/bin/python3
# -*- encode: utf-8 -*-

from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import json
import html
import logging
import re
import os
import sys

f=os.listdir("/var/www/html/sp-service/static/chat/")
patt2=re.compile('(.*).txt')
l1=[]
for i in f:
	l2=patt2.match(i)
	if not l2 == None:
		l1.append(l2.groups()[0])
e1=""
for i in l1:
	e1+='"'+i+'":set(),'
exec('ws_list={'+e1+'}')
patt1=re.compile('/chat/(.*)')

def chat_handle(environ, start_response, room):
	ws = environ['wsgi.websocket']
	ws_list[room].add(ws)
	print(ws)

	print('enter:', len(ws_list[room]), environ['REMOTE_ADDR'], environ['REMOTE_PORT'])
	while True:
		msg=ws.receive()
		if msg is None:
			break
		msg = json.loads(msg)
		if msg["message"] is None:
			break

		if msg["type"]=="start" or msg["type"]=="re":
			with open("/var/www/html/sp-service/static/chat/on/"+room+".txt",'a') as f:
				f.write(msg["user"]+"\n")

		elif msg["type"]=="leave":
			with open("/var/www/html/sp-service/static/chat/on/"+room+".txt",'r') as f:
				data=f.read()
			data1=data.split()
			while msg["user"] in data1:
				data1.remove(msg["user"])
			tmp4=""
			for i in data1:
				tmp4=i+"\n"
			with open("/var/www/html/sp-service/static/chat/on/"+room+".txt","w") as f:
				f.write(tmp4)

		msg={"message": html.escape(msg["message"]),"writer": msg["writer"],"user": msg["user"],"color": msg["color"],"type": msg["type"]}

		remove = set()
		for s in ws_list[room]:
			try:
				s.send(json.dumps(msg))
			except Exception:
				remove.add(s)

		for s in remove:
			ws_list[room].remove(s)
		if not msg["writer"]=="system":
			with open("/var/www/html/sp-service/static/chat/"+room+".txt",'r+') as f:
				d=f.read()
				f.seek(0)
				f.write('<div class="alert alert-'+msg["color"]+'">'+msg["writer"]+': '+msg["message"]+"</div>\n"+d)

	print('exit:', environ['REMOTE_ADDR'], environ['REMOTE_PORT'])
	ws_list[room].remove(ws)


def application(environ, start_response):
	path = environ['PATH_INFO']
	print('start:'+path)
	if path == '/chat':
		return chat_handle(environ, start_response,room="chat")
	d=patt1.findall(path)
	print('d='+d[0])
	if 	os.path.exists('/var/www/html/sp-service/static/chat/'+d[0]+'.txt'):
		return chat_handle(environ, start_response,room=d[0])
	else:
		start_response('404 Not Found.', [('Content-Type', 'text/plain')])
		return 'not found'


if __name__ == '__main__':
	server = pywsgi.WSGIServer(('127.0.0.1', 9250), application, handler_class=WebSocketHandler)
	print("Starting Gevent Websocket Server.")
	server.serve_forever()
