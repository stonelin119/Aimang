from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])  # 可以直接把对象里面的配置数据转换到app.config里面
	config[config_name].init_app(app)

	db.init_app(app)

	# 路由和其他处理程序定义

	from .main.views import auth, log, setting
	app.register_blueprint(auth.bp)
	app.register_blueprint(setting.bp)

	app.register_blueprint(log.bp)
	app.add_url_rule('/', endpoint='log.index')

	return app
