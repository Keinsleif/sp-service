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

logger=application.logger
logger.setLevel(logging.INFO)

db_util.init_app(application)


@application.route('/sp-service/')
def index():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		return routing.show_home()

@application.route('/sp-service/sp-user/login', methods=['GET','POST'])
def login():
	result=routing.check_login()
	if result==False:
		if request.method=='POST':
			return routing.do_login()
		elif request.method=='GET':
			return routing.show_login()
	else:
		return redirect(url_for('logout'))

@application.route('/sp-service/sp-user/logout', methods=['GET','POST'])
def logout():
	result=routing.check_login()
	if result==False:
		return redirect(url_for("login"))
	else:
		if request.method=='POST':
			return routing.do_logout(result)
		elif request.method=='GET':
			return routing.show_logout(result)

@application.route('/sp-service/sp-user/signup',methods=['GET','POST'])
def signup():
	if request.method=='POST':
		return routing.do_signup()
	elif request.method=='GET':
		return routing.show_signup()

@application.route('/sp-service/contact',methods=['GET','POST'])
def contact():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_contact_form()
		elif request.method=='POST':
			return routing.do_contact_form(result)

@application.route('/sp-service/upload',methods=['GET','POST'])
def upload():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_upload()
		elif request.method=='POST':
			return routing.do_upload(result)

@application.route('/sp-service/threads',methods=['GET'])
def threads():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_threads()

@application.route('/sp-service/threads/new',methods=['GET','POST'])
def create_thread():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_new_thread()
		elif request.method=='POST':
			return routing.do_new_thread(result)

@application.route("/sp-service/thread/<string:thread>",methods=['GET','POST'])
def board_render(thread):
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_board(result,thread)
		elif request.method=='POST':
			return routing.do_post_to_board(result,thread)

@application.route("/sp-service/sp-user/mypage",methods=['GET','POST'])
def mypage():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_mypage(result)

@application.route("/sp-service/chat",methods=['GET'])
def chat():
	result=routing.check_login()
	if result==False:
		return redirect(url_for('login'))
	else:
		if request.method=='GET':
			return routing.show_chat(result)

@application.route("/sp-service/ip",methods=['GET'])
def ip():
	return routing.show_ip()


#=====================Admin Page ==============================#


@application.route('/sp-service/sp-admin',methods=['GET'])
def sp_admin():
	if request.method=='GET':
		return admin.show_admin()

@application.route('/sp-service/sp-admin/user',methods=['GET'])
def user_list():
	if request.method=='GET':
		return admin.show_user_list()

@application.route('/sp-service/sp-admin/user/upgrade',methods=['GET','POST'])
def upgrade_user():
	if request.method=='GET':
		return admin.show_del_up_user('upgrade')
	if request.method=='POST':
		return admin.do_del_up_user('upgrade')

@application.route('/sp-service/sp-admin/user/delete',methods=['GET','POST'])
def delete_user():
	if request.method=='GET':
		return admin.show_del_up_user('delete')
	if request.method=='POST':
		return admin.do_del_up_user('delete')

@application.route('/sp-service/sp-admin/user/edit',methods=['GET','POST'])
def edit_user():
	if request.method=='GET':
		return admin.show_edit_user()
	if request.method=='POST':
		return admin.do_edit_user()

@application.route('/sp-service/sp-admin/contact',methods=['GET'])
def list_contact():
	if request.method=='GET':
		return admin.show_contact()

@application.route('/sp-service/sp-admin/contact/delete',methods=['GET','POST'])
def delete_contact():
	if request.method=='GET':
		return admin.show_delete_contact()
	elif request.method=='POST':
		return admin.do_delete_contact()


application.before_request(routing.before_request)
application.after_request(routing.after_request)

application.register_error_handler(Exception, dfn_error.exception_handler)
application.register_error_handler(404, dfn_error.not_found_handler)
application.register_error_handler(werkzeug.exceptions.RequestEntityTooLarge,dfn_error.over_max_file_size_handler)

