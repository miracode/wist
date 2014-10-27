# -*- coding: utf-8 -*-
from flask import Flask
from flask import g
from flask import abort
from flask import request
from flask import url_for
from flask import redirect
from flask import session
import os
import psycopg2
from contextlib import closing
from passlib.hash import pbkdf2_sha256

# TODO: add lists.owner_id constraint
# TODO: add list_id constraint for list_items and list_users
DB_SCHEMA = """
DROP TABLE IF EXISTS lists;
CREATE TABLE lists (
    list_id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    description TEXT,
    owner_id INT
);
CREATE TABLE users (
    user_id serial PRIMARY KEY,
    user_name VARCHAR (127) NOT NULL,
    user_info TEXT,
    icon_color TEXT);
CREATE TABLE list_items (
    list_id INT,
    item_id serial PRIMARY KEY,
    text TEXT NOT NULL,
    checked INT NOT NULL
    );
CREATE TABLE list_users (
    list_id INT,
    user_id INT)
"""
DB_LIST_INSERT = """
INSERT INTO lists (title, description, owner_id) values (%s, %s, %s)
"""
# TODO add where user_id = id
DB_ALL_USER_LISTS = """
SELECT list_id, title, description FROM lists ORDER BY list_id
"""

app = Flask(__name__)

app.config['DATABASE'] = os.environ.get('DATABASE_URL',
                                        'dbname=wist user=Michelle')
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD',
                                              pbkdf2_sha256.encrypt('admin'))
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'soopersekret')


def connect_db():
    """Return connection to configured db"""
    return psycopg2.connect(app.config['DATABASE'])


def init_db():
    """Initialize database using DB_SCHEMA"""
    with closing(connect_db()) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        if exception and isinstance(exception, psycopg2.Error):
            # rollback if any errors
            db.rollback()
        else:
            # otherwise, good to commit
            db.commit()
        db.close()


def make_list(title, description, user_id):
    # User does not input user_id, this comes from login info
    if not user_id:
        raise ValueError("User required to create a list")
    # User needs to supply a title, but no description is OK
    if not title or not user_id:
        raise ValueError("Title required to create a list")
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_INSERT, [title, description, user_id])


def get_all_lists():
    """return a list of all lists as dicts"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ALL_USER_LISTS)
    keys = ('list_id', 'title', 'description', 'owner_id')
    return [dict(zip(keys, row)) for row in cur.fetchall()]


@app.route('/')
def show_lists():
    lists = get_all_lists()
    output = u""
    for l in lists:
        output += u'Title: %s\nDescription: %s\n\n' % (l['title'],
                                                       l['description'])
    if output == u"":
        output = u"No lists here so far"
    return output


@app.route('/add', methods=['POST'])
def add_list():
    try:
        make_list(request.form['title'], request.form['description'], '1234')
    except psycopg2.Error:
        abort(500)
    return redirect(url_for('show_lists'))


def do_login(username='', passwd=''):
    if username != app.config['ADMIN_USERNAME']:
        raise ValueError
    if not pbkdf2_sha256.verify(passwd, app.config['ADMIN_PASSWORD']):
        raise ValueError
    session['logged_in'] = True


def login():
    error = None
    if request.method == 'POST':
        try:
            do_login(request.form['username'].encode('utf-8'),
                     request.form['password'].encode('utf-8'))
        except ValueError:
            error = "Login Failed"
        else:
            return redirect(url_for('show_entries'))
    # TODO: Implement once we have templates
    # return render_template('login.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
