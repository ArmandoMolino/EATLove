from flask import Flask, url_for, redirect

import os, Home, Auth, Place, User

from DataBase import DataBase


def create_app(test_config=None):
    # crea e configura l'app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # carica i config, quando non si sta testando
        app.config.from_pyfile('config.py', silent=True)
    else:
        # carica i config passati in input
        app.config.update(test_config)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # registra i comandi del database
    DataBase.init_app(app)

    # registra tutti i blueprint
    app.register_blueprint(Home.bp)
    app.register_blueprint(Auth.bp)
    app.register_blueprint(Place.bp)
    app.register_blueprint(User.bp)

    # una pagina che ci ridirige verso /home
    @app.route('/')
    def prova():
        return redirect(url_for('Home.home'))

    return app


if __name__ == '__main__':
    create_app().run()
