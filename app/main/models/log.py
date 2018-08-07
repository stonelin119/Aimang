from ... import db


class Log(db.Model):
	log_id = db.Column(db.Integer, primary_key=True, nullable=False)
	msg = db.column(db.String(1024))
	priority = db.Column(db.Text)
	dst = db.Column(db.String(128))
	dstport = db.Column(db.String(30))
	src = db.Column(db.String(128))
	srcport = db.Column(db.String(30))
	timestamp = db.Column(db.DATETIME)


class Last24Hour(Log):
	pass


class Last7Day(Log):
	pass
