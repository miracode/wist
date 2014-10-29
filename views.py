# -*- coding: utf-8 -*-
from flask import Flask
from flask import g
from flask import render_template
from flask import abort
from flask import request
from flask import url_for
from flask import redirect
from flask import session
import os
import psycopg2
from contextlib import closing
from passlib.hash import pbkdf2_sha256
from database import *


def do_login(db_pwd, user_id, username='', passwd=''):
    if passwd != db_passwd:
        raise ValueError
    session['logged_in'] = True
    session['user_id'] = user_id


@app.route('/')
def show_login():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def register():
    if request.form['toggle'] == 'register':
        insert_user(request.form['username'], pbkdf2_sha256.encrypt(request.form['password']), request.form['email'])
        return('You registered')
    else:
        
        return('You tried to log in')


@app.route('/lists/all', methods=['GET'])
def show_lists():
    return render_template('list_all.html')


@app.route('/lists/view')
def display_list():
    return render_template('list_view.html')


@app.route('/lists/create', methods=['GET', 'POST'])
def create_list():
    make_list(request.form['list-title'], request.form['list-description'], request.form['user_id'])
    return('YOU MADE A WIST!')


@app.route('/lists/item/check', methods=['GET', 'POST'])
def check_item():
    #update_item_checkmark(checked, list_id, item_id) <--boolean?
    return('YOU CHECKED A THING')


@app.route('/lists/item/add', methods=['GET', 'POST'])
def add_item():
    #insert_list_item(list_id, request.form['list-item-title'])
    return('YOU ADDED A THING!')


@app.route('/lists/item/remove', methods=['GET', 'POST'])
def remove_item():
    #delete_list_item(list_id, item_id)
    return('YOU DELETED A THING!')

if __name__ == '__main__':
    app.run(debug=True)
