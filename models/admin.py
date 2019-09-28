#!/var/www/venv/bin/python
# -*- coding: utf-8 -*-

from flask import request, current_app, logging, render_template, redirect, url_for, make_response, flash
from flask_bcrypt import check_password_hash, generate_password_hash
from models import db_util



def show_admin():
	return render_template("admin.html")

def show_user_list():
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_user;")
	result=cur.fetchall()
	return render_template('user_list.html',users=result)

def show_del_up_user(cont):
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_user;")
	result=cur.fetchall()
	return render_template(cont+'_user.html',users=result)

def do_del_up_user(cont):
	db=db_util.get_db()
	cur=db.cursor()
	user_id=request.form.getlist(cont)
	if not user_id==[]:
		for i in user_id:
			if cont=='upgrade':
				cur.execute("update sp_user set type='normal' where id=%s",(i,))
			elif cont=='delete':
				cur.execute("delete from sp_user where id=%s",(i,))
		db.commit()
		cur.execute("select * from sp_user;")
		result=cur.fetchall()
		cur.close()
		flash("User is successful "+cont+"ed.","alert alert-success")
		return redirect(url_for('user_list'))
	else:
		cur.execute("select * from sp_user;")
		result=cur.fetchall()
		cur.close()
		flash("Not Selected Users!","alert alert-danger")
		return render_template(cont+'_user.html',users=result)

def show_edit_user(uname):
	db=db_util.get_db()
	cur=db.cursor()
	return render_template('edit_user.html',user=uname)

def do_edit_user():
	db=db_util.get_db()
	cur=db.cursor()


def show_contact():
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_contact;")
	result=cur.fetchall()
	return render_template('contact_list.html',contents=result)

def show_delete_contact():
	db=db_util.get_db()
	cur=db.cursor()
	cur.execute("select * from sp_contact;")
	result=cur.fetchall()
	return render_template('delete_contact.html',contents=result)

def do_delete_contact():
	db=db_util.get_db()
	cur=db.cursor()
	user_id=request.form.getlist("delete")
	if not user_id==[]:
		for i in user_id:
			cur.execute("delete from sp_contact where id=%s",(i,))
		db.commit()
		cur.execute("select * from sp_contact;")
		result=cur.fetchall()
		cur.close()
		flash("Contact is successful deleted.","alert alert-success")
		return redirect(url_for('list_contact'))
	else:
		cur.execute("select * from sp_contact;")
		result=cur.fetchall()
		cur.close()
		flash("Not Selected Contacts!","alert alert-danger")
		return render_template('delete_contact.html',contents=result)
