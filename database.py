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

# INITIALIZE DATABASE
# This will drop all tables and re-initialize the database
# Note constraints on tables.  Colors table is initialized with
# values here also.
DB_SCHEMA = """
DROP TABLE IF EXISTS list_users;
DROP TABLE IF EXISTS list_items;
DROP TABLE IF EXISTS lists;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS colors;
CREATE TABLE colors (
    color TEXT PRIMARY KEY
);
CREATE TABLE users (
    user_id serial PRIMARY KEY,
    user_name VARCHAR (127) NOT NULL,
    user_passwd VARCHAR (127) NOT NULL,
    user_email TEXT UNIQUE NOT NULL,
    user_info TEXT,
    icon_color TEXT REFERENCES colors (color)
);
CREATE TABLE lists (
    list_id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    description TEXT,
    owner_id INT REFERENCES users (user_id)
);
CREATE TABLE list_items (
    list_id INT NOT NULL REFERENCES lists (list_id),
    item_id serial NOT NULL,
    text TEXT NOT NULL,
    checked INT NOT NULL,
    PRIMARY KEY (list_id, item_id),
    CHECK (checked in (0, 1))
);
CREATE TABLE list_users (
    list_id INT REFERENCES lists (list_id),
    user_id INT REFERENCES users (user_id)
);
INSERT INTO colors VALUES ('green');
INSERT INTO colors VALUES ('blue');
INSERT INTO colors VALUES ('purple');
"""
# DB INSERT statements
DB_USER_INSERT = """
INSERT INTO users (user_name, user_passwd, user_email) values (%s, %s, %s)
"""
DB_LIST_INSERT = """
INSERT INTO lists (title, description, owner_id) values (%s, %s, %s)
"""
DB_LIST_ITEM_INSERT = """
INSERT INTO list_items (list_id, text, checked) VALUES (%s, %s, 0)
"""
DB_LIST_USER_INSERT = """
INSERT INTO list_users (list_id, user_id) VALUES (%s, %s)
"""
# DB SELECT statements
DB_ALL_USER_LISTS = """
SELECT list_id, title, description FROM lists
WHERE owner_id = %s
ORDER BY list_id
"""
DB_ALL_LIST_ITEMS = """
SELECT item_id, text, checked FROM list_items
WHERE list_id = %s
"""
DB_ALL_LIST_USERS = """
SELECT user_id FROM list_users WHERE list_id = %s
"""
DB_USER_SELECT_BY_NAME = """
SELECT user_id, user_passwd FROM users WHERE user_name = %s
"""
# DB UPDATE statements
DB_USER_INFO_UPDATE = """
UPDATE users
SET user_info = %s
WHERE user_id = %s
"""
DB_USER_COLOR_UPDATE = """
UPDATE users
SET icon_color = %s
WHERE user_id = %s
"""
DB_LIST_TITLE_TEXT_UPDATE = """
UPDATE lists
SET title = %s,
    description = %s
WHERE list_id = %s
"""
DB_LIST_ITEM_CHECK_UPDATE = """
UPDATE list_items
SET checked = %s
WHERE list_id = %s
AND item_id = %s
"""
# DELETE statements
DB_LIST_ITEM_DELETE = """
DELETE from list_items
WHERE list_id = %s
AND item_id = %s
"""
DB_LIST_DELETE = """
DELETE FROM list_items
WHERE list_id = %s;
DELETE FROM lists
WHERE list_id = %s
"""
DB_LIST_USER_DELETE = """
DELETE FROM list_users
WHERE list_id = %s
AND user_id = %s
"""
DB_USER_DELETE = """
DELETE from list_users
WHERE user_id = %s;
DELETE from lists
WHERE owner_id = %s;
DELETE FROM users
where user_id = %s;
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

"""
DB INSERTS
"""


def insert_user(name, passwd, email):
    """insert a user's name, password, and email; generate an ID"""
    if not name:
        raise ValueError("User name required to create user")
    if not passwd:
        raise ValueError("User password required to create user")
    if not email:
        raise ValueError("User email required to create user")
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_USER_INSERT, [name, passwd, email])


def make_list(title, description, user_id):
    """Make an empty list for user with a title and description"""
    # User does not input user_id, this comes from login info
    if not user_id:
        raise ValueError("User required to create a list")
    # User needs to supply a title, but no description is OK
    if not title or not user_id:
        raise ValueError("Title required to create a list")
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_INSERT, [title, description, user_id])


def insert_list_item(list_id, text):
    """Add an unchecked item to a list"""
    if not list_id:
        raise ValueError("List must be specified")
    if not text:
        raise ValueError("List item must contain text")
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_ITEM_INSERT, [list_id, text])


def add_list_user(list_id, user_id):
    """Add a user to a list by the list_id and their user_id"""
    if not list_id:
        raise ValueError("List must be specified")
    if not user_id:
        raise ValueError("User must be specified")
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_USER_INSERT, [list_id, user_id])

"""
DB SELECTS/RETURNS
"""

def get_login_user(user_name):
    """Attempts to return the password and user id searching by username"""
    con = get_database_connection()
    cur = con.cursor()


def get_all_users_lists(user_id):
    """Return a list of all the user's lists as dicts"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ALL_USER_LISTS, [user_id])
    keys = ('list_id', 'title', 'description')
    return [dict(zip(keys, row)) for row in cur.fetchall()]


def get_all_list_items(list_id):
    """Return a list of specified list's items as dicts"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ALL_LIST_ITEMS, [list_id])
    keys = ('item_id', 'text', 'checked')
    return [dict(zip(keys, row)) for row in cur.fetchall()]


def get_all_list_users(list_id):
    """Return users of a given list as dicts"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ALL_LIST_USERS, [list_id])
    keys = [u'list_id']
    return [dict(zip(keys, row)) for row in cur.fetchall()]

"""
DB UPDATES
"""


def update_user_info(user_info, user_id):
    """Update the user's information text"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_USER_INFO_UPDATE, [user_info, user_id])


def user_color_update(color, user_id):
    """Update user icon color"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_USER_COLOR_UPDATE, [color, user_id])


def update_list_title_text(title, description, list_id):
    """Update a lists title and description"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_TITLE_TEXT_UPDATE, [title, description, list_id])


def update_item_checkmark(checked, list_id, item_id):
    """Update list item checkmark"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_ITEM_CHECK_UPDATE, [checked, list_id, item_id])

"""
DB DELETIONS
"""


def delete_list_item(list_id, item_id):
    """Delete an item from a list"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_ITEM_DELETE, [list_id, item_id])


def delete_list(list_id):
    """Delete an entire list"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_DELETE, [list_id, list_id])


def delete_list_user(list_id, user_id):
    """Remove a user's permission to a list"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_LIST_USER_DELETE, [list_id, user_id])


def delete_user(user_id):
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_USER_DELETE, [user_id, user_id, user_id])


# @app.route('/')
# def show_lists(user_id):
#     lists = get_all_users_lists(user_id)
#     output = u""
#     for l in lists:
#         output += u'Title: %s\nDescription: %s\n\n' % (l['title'],
#                                                        l['description'])
#     if output == u"":
#         output = u"No lists here so far"
#     return output


# @app.route('/add', methods=['POST'])
# def add_list():
#     try:
#         make_list(request.form['title'], request.form['description'], '1234')
#     except psycopg2.Error:
#         abort(500)
#     return redirect(url_for('show_lists'))


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
