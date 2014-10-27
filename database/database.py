# -*- coding: utf-8 -*-
import flask
from flask import Flask
from flask import g
import os
import psycopg2
from contextlib import closing

# TODO: add owner_id constraint
DB_SCHEMA = """
DROP TABLE IF EXISTS lists;
CREATE TABLE lists (
    list_id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    description TEXT,
    owner_id INT
)
"""

app = Flask(__name__)

app.config['DATABASE'] = os.environ.get('DATABASE_URL',
                                        'dbname=wist user=Michelle')


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
    if not db:
        g.db = db = connect_db()
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db:
        if exception and isinstance(exception, psycopg2.Error):
            # rollback if any errors
            db.rollback()
        else:
            # otherwise, good to commit
            db.commit()
        db.close()


@app.route('/')
def welcome():
    return u"Welcome to Wist"

if __name__ == '__main__':
    app.run(debug=True)
