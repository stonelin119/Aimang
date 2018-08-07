import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from werkzeug.exceptions import abort

from ..models.auth import User
from ... import db
from sqlalchemy import or_


bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_user(user_id, check_auth=True):
	user = User.query.filter_by(id=user_id).first()

	if user is None:
		abort(404, "User id {0} doesn't exist.".format(user_id))

	if check_auth and g.user.user_type != 1:
		abort(403)

	return user


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = User.query.filter_by(id=user_id).first()


@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		user_name = request.form['user_name']
		password = request.form['password']
		error = None

		user = User.query.filter_by(user_name=user_name).first()
		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user.password_hash, password):
			error = 'Incorrect password.'

		if error is None:
			session.clear()
			session['user_id'] = user.id
			return redirect(url_for('index'))

		flash(error)

	return render_template('auth/login.html')


@bp.route('/list')
def user_list():
	users = User.query.all()

	return render_template('auth/user_list.html', users=users)


@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		user_name = request.form['user_name']
		email = request.form['email']
		password = request.form['password']

		error = None
		if not user_name:
			error = 'User name is required.'
		elif not email:
			error = 'email is required.'
		elif not password:
			error = 'Password is required.'
		elif User.query.filter(or_(User.user_name == user_name, User.email == email)).first() is not None:
			error = 'User {} or email {} is already registered.'.format(user_name, email)

		if error is None:
			user = User(user_name, email, password)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('auth.user_list'))

		flash(error)

	return render_template('auth/user.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
	user = get_user(id)

	if request.method == 'POST':
		user_name = request.form['user_name']
		email = request.form['email']
		status = request.form['status']

		error = None

		if not user_name:
			error = 'User name is required.'
		elif not email:
			error = 'email is required.'

		if error is None:
			user.user_name = user_name
			user.email = email
			user.status = status

			db.session.commit()

			return redirect(url_for('auth.user_list'))

		flash(error)

	return render_template('auth/user.html', user=user)


@bp.route('/<int:id>/update_password', methods=('GET', 'POST'))
def update_password(id):
	user = get_user(id)

	if request.method == 'POST':
		password = request.form['password']

		error = None

		if not password:
			error = 'password is required.'

		if error is None:
			user.password = password

			db.session.commit()

			return redirect(url_for('auth.user_list'))

		flash(error)

	return render_template('auth/user_password.html', user=user)


@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
	user = get_user(id)

	db.session.delete(user)
	db.session.commit()

	return redirect(url_for('auth/list'))
