import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    # g : 각 리퀘스트마다 유일한 객체. 리퀘스트동안 여러번 접근되는 데이터를 담아두는 객체
    # current_app : 리퀘스트를 다루고있는 플라스크 어플리케이션 객체.
    # sqlite3.Row : 결과값을 딕셔너리로 리턴한다고 커넥션에 알림. 열값을 이름으로 접근할 수 있다.
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    # open_resource : tutorial패키지에 있는 관련 리소스를 연다.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# init-db 커맨드 라인 명령을 정의함.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    # teardown_appcontext : 리스폰스를 넘겨준 후 정리할 때 실행할 함수를 알려준다.
    # add_command : 플라스크 명령어와 함게 실행 될 명령을 추가한다. 팩토리에서 호출한다.
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)