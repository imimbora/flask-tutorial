import os
from flask import Flask


def create_app(test_config=None):
    """
    어플리케이션 팩토리 함수.
    :param test_config:
    :return:
    """
    # create and configure the app
    # instance_relative_config: 앱에게 인스턴스 폴더에 설정파일(로컬에서 사용하는 db설정파일 등)이 있다고 알림. 인스턴스 폴더는 프로젝트 루트경로를 뜻함.
    app = Flask(__name__, instance_relative_config=True)

    # from_mapping 앱이 사용할 기본 설정 셋팅
    # SECRET_KEY : 플라스크와 확장 프로그램에 의해 데이터를 보호하기 위해 사용됨. 배포 시 랜덤값이 들어가야함.
    # DATABASE : SQLLITE DB 파일이 저장될 경로.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask.sqlite')
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        # from_pyfile : 인스턴스 폴더에 있는 config.py 모듈을 받는다(있는 경우).
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        # 인스턴스 경로가 존재하는지 확인한다. 경로를 자동으로 만들지는 않음.
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    # from . import auth
    # app.register_blueprint(auth.bp)
    #
    # from . import blog
    # app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')

    return app