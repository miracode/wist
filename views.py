# -*- coding: utf-8 -*-
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import session
from passlib.hash import pbkdf2_sha256
from database import *


def do_login(db_pwd, user_id, username='', passwd=''):
    if username not in get_all_user_names():
        raise ValueError("Invalid Username or Password")
    if not pbkdf2_sha256.verify(passwd, db_pwd):
        raise ValueError("Invalid Username or Password")
    session['logged_in'] = True
    session['user_id'] = user_id


# def verify_login(func):
#     def wrapper(*args, **kwargs):
#         if not session['logged_in']:
#             return redirect(url_for('show_login'))
#         else:
#             func(*args, **kwargs)
#     return wrapper


@app.route('/')
def show_login():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        try:
            if request.form['toggle'] == 'register':
                return new_register()
            else:
                return login()
        except ValueError:
            error = "Invalid Username or Password"
    return render_template('login.html', error=error)


def new_register():
    insert_user(request.form['username'],
                pbkdf2_sha256.encrypt(request.form['password']),
                request.form['email'])
    user_data = get_login_user(request.form['username'])
    do_login(user_data[0]['user_passwd'], user_data[0]['user_id'],
             request.form['username'], request.form['password'])
    return redirect(url_for('show_lists'))


def login():
    user_data = get_login_user(request.form['username'])
    if user_data == []:
        raise ValueError
    do_login(user_data[0]['user_passwd'], user_data[0]['user_id'],
             request.form['username'], request.form['password'])
    if session['logged_in']:
        return redirect(url_for('show_lists'))


@app.route('/lists/all', methods=['GET'])
def show_lists():
    lists = get_all_users_lists(session['user_id'])
    user = get_user_name(session['user_id'])
    message = "%s's Lists" % user
    return render_template('list_all.html', lists=lists,
                    message=message, user_id=session['user_id'])


# This doesn't work
@app.route('/lists/all', methods=['GET'])
def show_lists_register_sucess():
    lists = get_all_users_lists(session['user_id'])
    user = get_user_name(session['user_id'])
    message = "Thank you for registering %s!" % user
    return render_template('list_all.html', lists=lists,
                    message=message, user_id=session['user_id'])


@app.route('/lists/<id>')
def display_list(id):
    items = get_all_list_items(id)
    this_list = get_list_info(id)[0]
    owner = get_user_name(this_list['owner_id'])[0]
    return render_template('list_view.html', items=items, this_list=this_list,
                           list_id=id, owner=owner, user_id=session['user_id'])


@app.route('/lists/create', methods=['GET', 'POST'])
def create_list():
    make_list(request.form['list-title'], request.form['list-description'],
              session['user_id'])
    return redirect(url_for('show_lists', user_id=session['user_id']))


@app.route('/lists/delete', methods=['GET', 'POST'])
def remove_list():
    list_id = request.form.get('list_id', 0, type=int)
    delete_list(list_id)
    return('DELETED')


@app.route('/lists/<list_id>/check', methods=['GET', 'POST'])
def check_item(list_id):
    item_id = request.form.get('item_id', 0, type=int)
    update_item_checkmark(1, list_id, item_id)
    return('YOU CHECKED A THING' + str(list_id) + ' ' + str(item_id))


@app.route('/lists/<id>/add', methods=['GET', 'POST'])
def add_item(id):
    insert_list_item(id, request.form['list-item-title'])
    return redirect(url_for('display_list', id=id, user_id=session['user_id']))


@app.route('/lists/<list_id>/remove', methods=['GET', 'POST'])
def remove_item(list_id):
    item_id = request.form.get('item_id', 0, type=int)
    delete_list_item(list_id, item_id)
    return redirect(url_for('display_list', id=list_id, user_id=session['user_id']))


@app.route('/lists/<list_id>/share', methods=['GET', 'POST'])
def share_list(list_id):
    user_name = request.form['shared_user']
    user_data = get_login_user(user_name)
    user_id = user_data[0]['user_id']
    add_list_user(list_id, user_id)
    return('YOU DID IT')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('show_login'))


@app.route('/profile/<user_id>')
def show_profile(user_id):
    user_name = get_user_name(user_id)
    return render_template('profile.html', user_name=user_name, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)
