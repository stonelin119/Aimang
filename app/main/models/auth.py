from ... import db
from werkzeug.security import generate_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80))
    password_hash = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Integer)
    user_type = db.Column(db.Integer)

    def __init__(self, user_name, email, password, status=0, user_type=0):
        self.user_name = user_name
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.status = status
        self.user_type = user_type

    def __repr__(self):
        return '<User %r>' % self.user_name
