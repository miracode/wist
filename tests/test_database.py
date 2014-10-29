# -*- coding: utf-8 -*-
from contextlib import closing
import pytest
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             os.pardir))
from database import app
from database import connect_db
from database import get_database_connection
from database import init_db
from flask import session

TEST_DSN = 'dbname=test_wist user=Michelle'
# Placeholder for "make a list" submit button
SUBMIT_BTN = '<input type="submit" value="Share" name="Share"/>'


def clear_db():
    with closing(connect_db()) as db:
        drop = """
DROP TABLE list_users;
DROP TABLE list_items;
DROP TABLE lists;
DROP TABLE users;
DROP TABLE colors;
"""
        db.cursor().execute(drop)
        db.commit()


@pytest.fixture(scope='session')
def test_app():
    """configure app for testing"""
    app.config['DATABASE'] = TEST_DSN
    app.config['TESTING'] = True


@pytest.fixture(scope='session')
def db(test_app, request):
    """initialize database schema and drop when finished"""
    init_db()

    def cleanup():
        clear_db()

    request.addfinalizer(cleanup)


@pytest.yield_fixture(scope='function')
def req_context(db):
    """run tests within a test request context so that 'g' is present"""
    with app.test_request_context('/'):
        yield
        con = get_database_connection()
        con.rollback()


def run_independent_query(query, params=[]):
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(query, params)
    return cur.fetchall()


def test_make_user(req_context):
    from database import insert_user
    expected = ("My Name", "My Password", "email@email.com")
    insert_user(*expected)
    rows = run_independent_query("SELECT * FROM users")
    assert len(rows) == 1
    for val in expected:
        assert val in rows[0]


def test_make_list(req_context):
    from database import insert_user
    from database import make_list
    insert_user("Test User", "pass", "email@email.com")
    user_id = run_independent_query("SELECT user_id FROM users")[0][0]
    expected = ("My Title", "My description", user_id)
    make_list(*expected)
    rows = run_independent_query("SELECT * FROM lists")
    assert len(rows) == 1
    for val in expected:
        assert val in rows[0]


def test_add_item(req_context):
    from database import insert_user
    from database import make_list
    from database import insert_list_item
    insert_user("Test User", "pass", "email@email.com")
    user_id = run_independent_query("SELECT user_id FROM users")[0][0]
    make_list("My Title", "My description", user_id)
    list_id = run_independent_query("SELECT * FROM lists")[0][0]
    expected = (list_id, "Item of a list")
    insert_list_item(*expected)
    rows = run_independent_query("SELECT * from list_items")
    assert len(rows) == 1
    for val in expected:
        assert val in rows[0]


def test_add_list_user(req_context):
    from database import insert_user
    from database import make_list
    from database import add_list_user
    insert_user("Test User", "pass", "email@email.com")
    insert_user("Another User", "pass", "happy@email.com")
    user_id1 = run_independent_query("SELECT user_id FROM users")[0][0]
    user_id2 = run_independent_query("SELECT user_id FROM users")[1][0]
    make_list("My Title", "My description", user_id1)
    list_id = run_independent_query("SELECT * FROM lists")[0][0]
    expected = (list_id, user_id2)
    add_list_user(*expected)
    rows = run_independent_query("SELECT * FROM list_users")
    assert len(rows) == 1
    for val in expected:
        assert val in rows[0]


def test_get_all_lists_empty(req_context):
    from database import insert_user
    from database import get_all_users_lists
    insert_user("Test User", "pass", "email@email.com")
    user_id = run_independent_query("SELECT user_id FROM users")[0][0]
    lists = get_all_users_lists(user_id)
    assert len(lists) == 0


def test_get_all_lists(req_context):
    from database import get_all_users_lists, make_list, insert_user
    insert_user("Test User", "pass", "email@email.com")
    user_id = run_independent_query("SELECT user_id FROM users")[0][0]
    expected = ("My Title", "My description", user_id)
    make_list(*expected)
    lists = get_all_users_lists(user_id)
    assert len(lists) == 1
    for l in lists:
        assert expected[0] == l['title']
        assert expected[1] == l['description']


def test_get_all_list_users(req_context):
    from database import get_all_list_users, make_list, insert_user
    from database import add_list_user
    insert_user("Test User", "pass", "email@email.com")
    insert_user("Another User", "pass", "happy@email.com")
    user_id1 = run_independent_query("SELECT user_id FROM users")[0][0]
    user_id2 = run_independent_query("SELECT user_id FROM users")[1][0]
    make_list("My Title", "My description", user_id1)
    list_id = run_independent_query("SELECT * FROM lists")[0][0]
    print  list_id, user_id1, user_id2
    add_list_user(list_id, user_id2)
    actual = get_all_list_users(list_id)[0]['list_id']
    assert user_id2 == actual


def test_update_user_info(req_context):
    from database import insert_user, update_user_info
    insert_user("Test User", "password", "email@email.com")
    user_id = run_independent_query("SELECT user_id FROM users")[0][0]
    expected = ("This is my user info!", user_id)
    update_user_info(*expected)
    rows = run_independent_query("SELECT user_id, user_info FROM users")
    for val in expected:
        assert val in rows[0]
