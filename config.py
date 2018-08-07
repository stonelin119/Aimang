import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

	@staticmethod  # 此注释可表明使用类名可以直接调用该方法
	def init_app(app):  # 执行当前需要的环境的初始化
		pass


class DevelopmentConfig(Config):  # 开发环境
	DEBUG = True
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SQLALCHEMY_DATABASE_URI = \
		os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:example@www.cinbo.cn:4306/linfeng?charset=utf8'
	CONVERT_IP_URL = 'http://ip.taobao.com/service/getIpInfo.php?ip={ip}'
	EXTRANNET_PROC_NAME = 'WeChat'
	INTRANNET_PROC_NAME = 'Finder'
	RULE_UPDATE_FILE = '/Users/stone/Workspace/Private/艾芒/数据/ruleupdate.sh'
	LOG_UPLOAD_FILE = '/Users/stone/Workspace/Private/艾芒/数据/logupload.sh'
	CRONTAB_FILE = '/Users/stone/Workspace/Private/艾芒/数据/crontab'
	BIGEYE_CFG_FILE = '/Users/stone/Workspace/Private/艾芒/数据/bigeyecfg.ini'


class TestingConfig(Config):  # 测试环境
	TESTING = True
	SQLALCHEMY_DATABASE_URI = \
		os.environ.get('TEST_DATABASE_URL') or 'mysql+pymysql://root:example@www.cinbo.cn:4306/linfeng?charset=utf8'
	CONVERT_IP_URL = 'http://ip.taobao.com/service/getIpInfo.php?ip={ip}'
	EXTRANNET_PROC_NAME = 'WeChat'
	INTRANNET_PROC_NAME = 'Finder'
	RULE_UPDATE_FILE = '/Users/stone/Workspace/Private/艾芒/数据/ruleupdate.sh'
	LOG_UPLOAD_FILE = '/Users/stone/Workspace/Private/艾芒/数据/logupload.sh'
	CRONTAB_FILE = '/Users/stone/Workspace/Private/艾芒/数据/crontab'
	BIGEYE_CFG_FILE = '/Users/stone/Workspace/Private/艾芒/数据/bigeyecfg.ini'


class ProductionConfig(Config):  # 生产环境
	SQLALCHEMY_DATABASE_URI = \
		os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:example@www.cinbo.cn:4306/linfeng?charset=utf8'
	CONVERT_IP_URL = 'http://ip.taobao.com/service/getIpInfo.php?ip={ip}'
	EXTRANNET_PROC_NAME = 'WeChat'  # '/ROOT/RUNBIGEYE'
	INTRANNET_PROC_NAME = 'Finder'
	RULE_UPDATE_FILE = '/Users/stone/Workspace/Private/艾芒/数据/ruleupdate.sh'
	LOG_UPLOAD_FILE = '/Users/stone/Workspace/Private/艾芒/数据/logupload.sh'
	CRONTAB_FILE = '/Users/stone/Workspace/Private/艾芒/数据/crontab'
	BIGEYE_CFG_FILE = '/Users/stone/Workspace/Private/艾芒/数据/bigeyecfg.ini'  #'/ROOT/PYTHON BIGEYE_DAEMON.PY'


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}
