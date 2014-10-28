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


@app.route('/login')
def show_login():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    insert_user(request.form['username'], request.form['password'], request.form['email'])
    return('YOU DID IT')

if __name__ == '__main__':
    app.run(debug=True)
