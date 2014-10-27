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
