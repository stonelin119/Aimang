from ... import db


class NetworkSettingEnum(db.Enum):
	network_segment = 'network_segment'
	network_card = 'network_card'


class NetworkTypeEnum(db.Enum):
	intranet = 'intranet'
	extranet = 'extranet'


class Network(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	intranet_segment = db.Column(db.String(80), nullable=False)
	extranet_segment = db.Column(db.String(80), nullable=False)
	intranet_card = db.Column(db.String(80), nullable=False)
	extranet_card = db.Column(db.String(80), nullable=False)

	def __init__(self, intranet_segment, extranet_segment, intranet_card, extranet_card):
		self.intranet_segment = intranet_segment
		self.extranet_segment = extranet_segment
		self.intranet_card = intranet_card
		self.extranet_card = extranet_card


class Backup(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	step = db.Column(db.Integer, nullable=False)

	def __init__(self, step):
		self.step = step


class Upgrade(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	rule_upload_address = db.Column(db.String(80), nullable=False)
	rule_upgrade_time = db.Column(db.Time, nullable=False)
	threat_upload_address = db.Column(db.String(80), nullable=False)
	threat_upgrade_time = db.Column(db.Time, nullable=False)

	def __init__(self, rule_upload_address, rule_upgrade_time, threat_upload_address, threat_upgrade_time):
		self.rule_upload_address = rule_upload_address
		self.rule_upgrade_time = rule_upgrade_time
		self.threat_upload_address = threat_upload_address
		self.threat_upgrade_time = threat_upgrade_time


class Warning(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	level = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(80), nullable=False)

	def __init__(self, level, title):
		self.level = level
		self.title = title


class WarningEmail(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	email = db.Column(db.String(80), nullable=False)

	def __init__(self, email):
		self.email = email
