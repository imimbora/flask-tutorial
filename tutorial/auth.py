import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from tutorial.db import get_db

# Blueprint : 관련된 뷰와 코드들을 모아놓는 방법. 한 어플리케이션에 뷰와 코드들 직접 등록하는 것 보다 블루프린트로 등록하는것이 효율적이다.
#             그러면 블루프린트는 팩토리 함수에서 등록할 수 있다.

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'select id from user where username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'insert into user (username, password) values (?,?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        # 템플릿을 렌더링할 때 검색할 수 있는 메시지를 저장한다.
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # session : 세션은 요청간에 데이터를 저장하는 dict.
        #           데이터는 브라우저에 전송된 쿠키에 저장되고 브라우저는 후속 요청과 함께 쿠키를 보낸다. 플라스크는 훼손되지 않도록 데이터에 안전하게 서명한다.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# before_app_request : 어떤 url이 요청되든 간에 뷰 함수가 실행되기 전에 실행되는 함수.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# url_for() : 이름과 인수 기반으로 뷰페이지의 url을 만들어낸다. 뷰와 연관이 있는 이름은 endpoint로 불린다. 기본적으로 이것은 뷰 함수와 같다.