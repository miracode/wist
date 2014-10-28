# -*- coding: utf-8 -*-
from contextlib import closing
import pytest
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
        db.cursor().execute("DROP TABLE lists")
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


def test_make_list(req_context):
    from database import make_list
    expected = ("My Title", "My description", 1234)
    make_list(*expected)
    rows = run_independent_query("SELECT * FROM lists")
    assert len(rows) == 1
    for val in expected:
        assert val in rows[0]


def test_get_all_lists_empty(req_context):
    from database import get_all_lists
    lists = get_all_lists()
    assert len(lists) == 0


def test_get_all_lists(req_context):
    from database import get_all_lists, make_list
    expected = ("My Title", "My description", 1234)
    make_list(*expected)
    lists = get_all_lists()
    assert len(lists) == 1
    for l in lists:
        assert expected[0] == l['title']
        assert expected[1] == l['description']


def test_empty_listing(db):
    actual = app.test_client().get('/').data
    expected = "No lists here so far"
    assert expected in actual


@pytest.fixture(scope='function')
def with_list(db, request):
    from database import make_list
    expected = (u'Test Title', u'Test description', 1234)
    with app.test_request_context('/'):
        make_list(*expected)
        # manually commit to avoid rollback
        get_database_connection().commit()

    def cleanup():
        with app.test_request_context('/'):
            con = get_database_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM lists")
            # manually commit to avoice rollback
            con.commit()
    request.addfinalizer(cleanup)

    return expected


def test_listing(with_list):
    expected = with_list[:-1]  # cut off user_id
    actual = app.test_client().get('/').data
    for value in expected:
        assert value in actual


def test_add_list(db):
    list_data = {
        u'title': u'Great Title',
        u'description': u'Great description!',
        u'user_id': 1234
    }
    actual = app.test_client().post(
        '/add', data=list_data, follow_redirects=True).data
    assert 'No lists here so far' not in actual
    list_data.pop(u'user_id')  # don't need to asser user_id on page
    for expected in list_data.values():
        assert expected in actual


def test_do_login_success(req_context):
    username, password = ('admin', 'admin')
    from database import do_login
    assert 'logged_in' not in session
    do_login(username, password)
    assert 'logged_in' in session


def test_do_login_bad_password(req_context):
    username = 'admin'
    bad_pass = 'wrong'
    from database import do_login
    with pytest.raises(ValueError):
        do_login(username, bad_pass)


def test_do_login_bad_username(req_context):
    username = 'bad'
    password = 'admin'
    from database import do_login
    with pytest.raises(ValueError):
        do_login(username, password)


def login_helper(username, password):
    login_data = {
        'username': username, 'password': password
    }
    client = app.test_client()
    return client.post(
        '/login', data=login_data, follow_redirects=True)


def test_start_as_anonymous(db):
    client = app.test_client()
    anon_home = client.get('/').data
    # TODO: this test fails, need to implement IF statement in template
    assert SUBMIT_BTN not in anon_home


def test_login_success(db):
    username, password = ('admin', 'admin')
    response = login_helper(username, password)
    assert SUBMIT_BTN in response.data


def test_login_fails(db):
    username, password = ('admin', 'wrong')
    response = login_helper(username, password)
    assert 'Login Failed' in response.data
