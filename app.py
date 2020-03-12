#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

from flask import Flask,request,make_response,redirect,url_for
import logging
from models import routing, db_util, admin, dfn_error
import os
import werkzeug


application=Flask(__name__)

application.secret_key='e221ea3d6e97b9a3'
application.config['MAX_CONTENT_LENGTH']=1073741824

dfn_error.init_app(application)
db_util.init_app(application)


@application.route('/sp-service/')
def index():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		return routing.show_home()

@application.route('/sp-service/sp-user/login/', methods=['GET','POST'])
def login():
	if request.method=='POST':
		return routing.do_login()
	elif request.method=='GET':
		return routing.show_login()

@application.route('/sp-service/sp-user/logout/', methods=['GET','POST'])
def logout():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for("login",next=result[1]))
	else:
		if request.method=='POST':
			return routing.do_logout(result[1])
		elif request.method=='GET':
			return routing.show_logout(result[1])

@application.route('/sp-service/sp-user/signup/',methods=['GET','POST'])
def signup():
	if request.method=='POST':
		return routing.do_signup()
	elif request.method=='GET':
		return routing.show_signup()

@application.route('/sp-service/contact/',methods=['GET','POST'])
def contact():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_contact_form()
		elif request.method=='POST':
			return routing.do_contact_form(result[1])

@application.route('/sp-service/upload/',methods=['GET','POST'])
def upload():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_upload()
		elif request.method=='POST':
			return routing.do_upload(result[1])

@application.route('/sp-service/threads/',methods=['GET'])
def threads():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_threads()

@application.route('/sp-service/threads/new/',methods=['GET','POST'])
def create_thread():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_new_thread()
		elif request.method=='POST':
			return routing.do_new_thread(result[1])

@application.route("/sp-service/thread/<string:thread>/",methods=['GET','POST'])
def board_render(thread):
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_board(result[1],thread)
		elif request.method=='POST':
			return routing.do_post_to_board(result[1],thread)

@application.route("/sp-service/sp-user/mypage/",methods=['GET','POST'])
def mypage():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_mypage(result[1])

@application.route("/sp-service/sp-user/mypage/leave",methods=['POST'])
def leave():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=="POST":
			return routing.leave_user(result[1])

@application.route("/sp-service/chat/",methods=['GET'])
def chat():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_chat(result[1])

@application.route('/sp-service/chat/rooms/',methods=['GET'])
def rooms():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_rooms()

@application.route('/sp-service/chat/rooms/new/',methods=['GET','POST'])
def create_room():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_new_room()
		elif request.method=='POST':
			return routing.do_new_room(result[1])

@application.route("/sp-service/chat/room/<string:room>/",methods=['GET','POST'])
def room_render(room):
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_room(result[1],room)

@application.route("/sp-service/sp-user/mypage/file-del/",methods=['POST'])
def del_file():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='POST':
			return routing.do_del_file()

@application.route("/sp-service/view/",methods=['GET'])
def view():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return routing.show_view(result[1])


@application.route("/sp-service/ip/",methods=['GET'])
def ip():
	return routing.show_ip()


#=====================Static Files=============================#

@application.route("/sp-service/static/upload/<string:file>",methods=['GET'])
def download_upload_file(file):
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		return routing.download_file(file)

#=====================Admin Page ==============================#


@application.route('/sp-service/sp-admin/',methods=['GET'])
def sp_admin():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return admin.show_admin()

@application.route('/sp-service/sp-admin/user/',methods=['GET'])
def user_list():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return admin.show_user_list()

@application.route('/sp-service/sp-admin/user/upgrade/',methods=['GET','POST'])
def upgrade_user():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return admin.show_del_up_user('upgrade')
		if request.method=='POST':
			return admin.do_del_up_user('upgrade')

@application.route('/sp-service/sp-admin/user/delete/',methods=['GET','POST'])
def delete_user():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return admin.show_del_up_user('delete')
		if request.method=='POST':
			return admin.do_del_up_user('delete')

@application.route('/sp-service/sp-admin/contact/',methods=['GET'])
def list_contact():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return admin.show_contact()

@application.route('/sp-service/sp-admin/contact/delete/',methods=['GET','POST'])
def delete_contact():
	result=routing.check_login()
	if result[0]==False:
		return redirect(url_for('login',next=result[1]))
	else:
		if request.method=='GET':
			return admin.show_delete_contact()
		elif request.method=='POST':
			return admin.do_delete_contact()


application.before_request(routing.before_request)
application.after_request(routing.after_request)

application.register_error_handler(Exception, dfn_error.exception_handler)
application.register_error_handler(404, dfn_error.not_found_handler)
application.register_error_handler(werkzeug.exceptions.RequestEntityTooLarge,dfn_error.over_max_file_size_handler)

