# -*- coding: utf-8 -*-
from contextlib import closing
import pytest

from database import app
from database import connect_db
from database import get_database_connection
from database import init_db

TEST_DSN = 'dbname=test_wist user=Michelle'


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
