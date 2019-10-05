#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

from flask import request, current_app, logging, render_template, redirect, url_for, make_response, flash, send_from_directory
from flask_bcrypt import check_password_hash, generate_password_hash
from http import HTTPStatus
from models import db_util
from secrets import token_hex
from time import time
import datetime
import re
import os
import html
import yaml

with open("sp-service/config/env.conf","r") as f:
	data=yaml.load(f)
for i in data:
	exec(i+"='"+data[i]+"'")
patt1=re.compile('(@link:\\((.*?)\\):@)')

def prepare_response(response):
	di=dir(response)
	if 'set_cookie' not in di:
		response=make_response(response)
	response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
	response.headers['Content-Security-Policy'] = 'default-src \'self\' wss:;'
	response.headers['Content-Security-Policy'] = 'script-src mypcnotes.mydns.jp \'nonce-ZWMyNjQ3YzMyNDI5ODI5MWQ0ODE1NjlkY2UxODAzODc2ZGUzYWQ2OA\''
	response.headers['X-Content-Type-Options'] = 'nosniff'
	response.headers['X-Frame-Options'] = 'SAMEORIGIN'
	response.headers['X-XSS-Protection'] = '1; mode=block'
	return response

def check_login():
	cook=request.cookies.get('sp-session',None)
	if cook==None:
		return [False,request.path]
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute('select * from sp_session where sess_id=%s;',(cook,))
	result=cur.fetchall()
	if result==[]:
		cur.execute("delete from sp_session where sess_id=%s;",(cook,))
		db.commit()
		cur.close()
		return [False,request.path]
	if float(result[0][1])-int(time()) >= 604800:
		cur.execute("delete from sp_session where sess_id=%s;",(cook,))
		db.commit()
		cur.close()
		return [False,request.path]
	elif result[0][2]==None:
		cur.close()
		return 0
	else:
		cur.close()
		return [True,result[0][2]]


def show_home():
	return render_template('home.html',title="メインページ")

def show_login():
	path=request.args.get('next','/sp-service')
	return render_template('login.html',title="ログイン",error="",reqpath=path)

def do_login():
	db=db_util.get_db()
	cur=db.cursor()
	user=request.form['userName']
	passwd=request.form['password']
	next_path=request.form['path']
	cur.execute("select * from sp_user where name=%s;",(user,))
	result=cur.fetchall()
	if result==[]:
		cur.close()
		flash("ユーザーネームが違います","alert alert-danger")
		return  render_template('login.html',title="Login",)
	elif check_password_hash(result[0][3],passwd):
		cur.execute("delete from sp_session where user_id=%s;",(result[0][0],))
		db.commit()
		sessid=token_hex(4)
		cur.execute("insert into sp_session values (%s,%s,%s);",(sessid,int(time()),result[0][0]))
		db.commit()
		cur.close()
		response=make_response(redirect(next_path))
		response.set_cookie('sp-session',value=sessid,secure=True,httponly=True)
		return response
	else:
		cur.close()
		flash("パスワードが違います","alert alert-danger")
		return render_template('login.html',title="Login",)

def show_logout(userid):
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select name from sp_user where id=%s;",(userid,))
	result=cur.fetchall()
	cur.close()
	if result==[]:
		return render_template('logout.html',title="ログアウト",user=userid)
	else:
		user=result[0]
		return render_template('logout.html',title="ログアウト",user=result[0][0])

def do_logout(userid):
	db=db_util.get_db()
	cur=db.cursor()
	response=make_response(redirect(url_for('login')))
	response.set_cookie("sp-session","")
	cur.execute("delete from sp_session where user_id=%s;",(userid,))
	db.commit()
	cur.close()
	return response

def show_signup():
	return render_template('signup.html',title="新規登録")

def do_signup():
	#logger=logging.create_logger(current_app)
	db=db_util.get_db()
	cur=db.cursor()
	if 'X-Forwarded-For' in request.headers:
		ip_addr=request.headers.getlist("X-Forwarded-For")[0]
	else:
		ip_addr=request.remote_ip
	cur.execute("select * from sp_ip where addr=%s",(ip_addr,))
	result=cur.fetchall()
	if result==[] or result[0][1]-int(time())<=43200:
		newname=request.form['newname']
		newhandle=request.form['newhandle']
		inewpass=request.form['newpass']
		rinewpass=request.form['retypenewpass']
		if inewpass==rinewpass:
			newpass=generate_password_hash(inewpass).decode('utf-8')
		else:
			cur.close()
			flash("パスワードが一致しません","alert alert-danger")
			return redirect(url_for('signup'))
		color=request.form['color']
		cur.execute("select * from sp_user where name=%s",(newname,))
		nbol=cur.fetchall()
		cur.execute("select * from sp_user where handle=%s",(newhandle,))
		hbol=cur.fetchall()
		cur.execute("select * from sp_user where password=%s",(newpass,))
		pbol=cur.fetchall()
		error=""
		if not nbol==[]:
			error="そのユーザーネームは既に使用されています"
		elif len(newname)>10:
			error="ユーザーネームが長過ぎます"
		elif len(newname)<2:
			error="ユーザーネームが短すぎます"
		elif not hbol==[]:
			error="そのハンドルネームは既に使用されています。"
		elif len(newhandle)>10:
			error="ハンドルネームが長過ぎます"
		elif len(newhandle)<2:
			error="ハンドルネームが短すぎます"
		elif not pbol==[]:
			error="そのパスワードは既に使用されています。"
		elif len(newpass)<8:
			error="もっと長いパスワードを入力してください"
		if error=="":
			cur.execute("select * from sp_user;")
			id_in=len(cur.fetchall())+1
			cur.execute("insert into sp_user values (%s,%s,%s,%s,%s,%s)",(id_in,newname,newhandle,newpass,color,"tmp"))
			if 'X-Forwarded-For' in request.headers:
				ip=request.headers.getlist("X-Forwarded-For")[0]
			else:
				ip=request.remote_addr
			cur.execute("insert into sp_ip values (%s,%s)",(ip,int(time())))
			db.commit()
			cur.close()
			return render_template('complite.html',title="登録完了",message="登録が完了しました")
		else:
			cur.close()
			flash(error,"alert alert-danger")
			return render_template('signup.html',title="新規登録",error=error)
	else:
		cur.close()
		return render_template('ip_wait.html',title="Warning")

def show_upload():
	return render_template('file_upload.html',title="SP-FileUploader")

def do_upload(id):
	if 'uploadFile' not in request.files:
		flash("ファイルを選択してください","alert alert-danger")
		return redirect(url_for('upload'))
	file=request.files['uploadFile']
	fileName=file.filename
	if ''==fileName:
		flash("ファイルを選択してください","alert alert-danger")
		return redirect(url_for('upload'))
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_file")
	result=cur.fetchall()
	cur.execute("select * from sp_file where tfilename=%s",(fileName,))
	re18=cur.fetchall()
	if not re18==[]:
		fileName=fileName+'.1'
	saveFileName=token_hex(16)+".png"
	cur.execute("insert into sp_file values (%s,%s,%s,%s,%s)",(len(result),saveFileName,fileName,time(),id,))
	db.commit()
	file.save(os.path.join(UPLOAD_DIR, saveFileName))
	os.chmod(os.path.join(UPLOAD_DIR,saveFileName),0o644)
	cur.close()
	return render_template('complite.html',title="アップロード完了",message="ファイルは正常にアップロードされました")

def show_mypage(id):
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_user where id=%s",(id,))
	udata=cur.fetchall()
	cur.execute("select * from sp_file where user_id=%s",(id,))
	files=cur.fetchall()
	return render_template('mypage.html',title="Myページ",data=udata[0],files=files,datetime=datetime,UPLOAD_DIR=UPLOAD_DIR)

def show_threads():
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_board_thread")
	result=cur.fetchall()
	cur.close()
	return render_template('show_threads.html',title="スレッドリスト",threads=result)

def show_new_thread():
	return render_template('new_threads.html',title="スレッドを作成",tname="")

def do_new_thread(id):
	db=db_util.get_db()
	cur=db.cursor()
	tname=request.form['newtname']
	tdesc=request.form['newtdesc']
	if tname:
		cur.execute('select * from sp_board_thread where name=%s',(tname,))
		result=cur.fetchall()
		if not result==[]:
			flash("そのスレッドの名前は既に使われています","alert alert-danger")
			cur.close()
			return redirect(url_for("create_thread"))
		elif tdesc=="":
			tdesc="No Description."
		if result==[]:
			cur.execute("select * from sp_board_thread")
			result=cur.fetchall()
			cur.execute("insert into sp_board_thread values (%s,%s,%s,%s)",(len(result),tname,tdesc,id,))
			db.commit()
			cur.close()
			flash("スレッドは正常に作成されました","alert alert-success")
			return redirect(url_for("threads"))

def show_board(id,thread):
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_board_thread where name=%s",(thread,))
	result=cur.fetchall()
	if result==[]:
		flash("スレッドが見つかりません","alert alert-warning")
		cur.close()
		return redirect(url_for("threads"))
	else:
		cur.execute("select * from sp_board_post where th_id=%s",(result[0][0],))
		result=cur.fetchall()
		posts=[]
		for i in range(len(result)):
			cur.execute("select * from sp_user where id=%s",(result[i][6],))
			l4=cur.fetchall()
			posts.append(result[i]+l4[0])
		return render_template('board.html',title=thread,posts=posts,datetime=datetime)

def do_post_to_board(id,thread):
	db=db_util.get_db()
	cur=db.cursor()
	ptitle=request.form['ptitle']
	pmess=request.form['pmess']
	if 'X-Forwarded-For' in request.headers:
		pip=request.headers.getlist("X-Forwarded-For")[0]
	else:
		pip=request.remote_addr
	if ptitle=="" or pmess=="":
		flash("タイトルが必要です","alert alert-danger")
		cur.close()
		return redirect(url_for("board_render"))
	else:
		pmess=html.escape(pmess)
		d=patt1.findall(pmess)
		for i in d:
			pmess=re.sub(re.sub('\)','\)',re.sub('\(','\(',i[0])),linktag.format(url=html.escape(i[1])),pmess)
		pmess=re.sub('\n','<br>',pmess)
		cur.execute("select * from sp_board_thread where name=%s",(thread,))
		r1=cur.fetchall()
		cur.execute("select * from sp_board_post")
		result=cur.fetchall()
		cur.execute("insert into sp_board_post values (%s,%s,%s,%s,%s,%s,%s)",(len(result)+1,time(),ptitle,pmess,r1[0][0],pip,id,))
		db.commit()
		cur.close()
		return redirect("/sp-service/thread/"+thread)


def show_contact_form():
	return render_template('contact_form.html',title="Contact")

def do_contact_form(user_id):
	contact=request.form['contact']
	if not contact:
		flash("何か入力してください","alert alert-danger")
		return redirect(url_for("contact"))
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_contact;")
	result=cur.fetchall()
	cur.execute("insert into sp_contact values(%s,%s,%s);",(str(len(result)+1),contact,user_id,))
	db.commit()
	cur.close()
	return render_template("complite.html",title="リクエストは正常に送信されました")


def show_chat(id):
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_user where id=%s",(id,))
	result=cur.fetchall()
	with open('sp-service/static/chat/chat.txt','r') as f:
		mess=f.read()
	cur.close()
	return render_template('chat.html',title="チャット",user=result,mess=mess,path="")

def show_rooms():
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_chat_room")
	result=cur.fetchall()
	cur.close()
	return render_template('chat-room.html',title="ルームリスト",rooms=result)

def show_new_room():
	return render_template('new-room.html',title="ルームを作成",tname="")

def do_new_room(id):
	db=db_util.get_db()
	cur=db.cursor()
	rname=request.form['newtname']
	rdesc=request.form['newtdesc']
	if rname:
		cur.execute('select * from sp_chat_room where name=%s',(rname,))
		result=cur.fetchall()
		if not result==[]:
			flash("そのルームの名前は既に使われています","alert alert-danger")
			cur.close()
			return redirect(url_for("create_room"))
		elif rdesc=="":
			rdesc="No Description."
		if result==[]:
			cur.execute("select * from sp_board_thread")
			result=cur.fetchall()
			cur.execute("insert into sp_chat_room values (%s,%s,%s,%s)",(len(result),rname,rdesc,id,))
			db.commit()
			cur.close()
			with open("sp-service/static/chat/"+rname+'.txt','w') as f:
				pass
			flash("ルームは正常に作成されました","alert alert-success")
			return redirect(url_for("rooms"))

def show_room(id,room):
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_chat_room where name=%s",(room,))
	result=cur.fetchall()
	if result==[]:
		flash("ルームが見つかりません","alert alert-warning")
		cur.close()
		return redirect(url_for("rooms"))
	else:
		try:
			with open('sp-service/static/chat/'+str(result[0][0])+'.txt','r') as f:
				mess=f.read()
		except:
			with open('sp-service/static/chat/'+str(result[0][0])+'.txt','w+') as f:
				mess=""
		cur.execute("select * from sp_user where id=%s",(id,))
		user=cur.fetchall()
		return render_template('chat.html',title=room,mess=mess,user=user,path='/'+str(result[0][0]))

def do_del_file():
	db=db_util.get_db()
	cur=db.cursor()
	file_id=request.form['delfile']
	cur.execute("select * from sp_file where id=%s",(file_id,))
	result=cur.fetchall()
	if not result==[]:
		cur.execute("delete from sp_file where id=%s",(file_id,))
		db.commit()
		os.remove(UPLOAD_DIR+result[0][1])
		flash("ファイルは正常に削除されました","alert alert-success")
		cur.close()
		return redirect(url_for('mypage'))
	cur.close()
	flash("選択されたファイルは存在しません","alert alert-danger")
	return redirect(url_for('mypage'))

def show_ip():
	if 'X-Forwarded-For' in request.headers:
		ip=request.headers.getlist("X-Forwarded-For")[0]
	else:
		ip="not"
	return ip

def download_file(file):
	return send_from_directory(UPLOAD_DIR,file)

def before_request():
	logger=logging.create_logger(current_app)
	logger.info('start '+current_app.name+' :: '+str(request.json)+str(request.headers))

def after_request(response):
	logger=logging.create_logger(current_app)
	logger.info('end '+current_app.name+' :: httpStatusCode='+str(response._status_code)+',response=')
	return  prepare_response(response)

