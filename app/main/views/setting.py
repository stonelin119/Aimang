import psutil
import re
import os

from flask import (
	current_app, Blueprint, flash, redirect, render_template, request, jsonify, url_for
)

from ..models.setting import Backup, Network, Upgrade, Warning, WarningEmail
from ... import db
from .auth import login_required
from dateutil import parser
from datetime import datetime

bp = Blueprint('setting', __name__, url_prefix='/setting')


def update_file(file_path, search_pattern, replace_pattern, replace_data):
	file_data = list()

	with open(file_path, "r", encoding="utf-8") as file:
		for line in file:
			regex = re.compile(search_pattern)
			result = regex.search(line)
			if result is not None:
				file_data.append(re.sub(replace_pattern, replace_data, line))
			else:
				file_data.append(line)

	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(''.join(file_data))


def update_ip_file(file_path, ip):
	search_pattern = 'IP=(.*)'
	replace_pattern = '=(.*)'
	replace_data = '={IP}'.format(IP=ip)

	update_file(file_path, search_pattern, replace_pattern, replace_data)


def update_ruleupdate_file(ip):
	file_path = current_app.config.get('RULE_UPDATE_FILE')

	update_ip_file(file_path, ip)


def update_logupload_file(ip):
	file_path = current_app.config.get('LOG_UPLOAD_FILE')

	update_ip_file(file_path, ip)


def update_crontab_file(logupload_time, ruleupdate_time):
	file_path = current_app.config.get('CRONTAB_FILE')

	search_pattern = '(.*)/logupload'
	replace_pattern = '(\s{2})(\d+)(\s{2})(\d+)(\s{2})'
	time_list = logupload_time.split(':')
	replace_data = '  {minute}  {hour}  '.format(minute=int(time_list[1]), hour=int(time_list[0]))
	update_file(file_path, search_pattern, replace_pattern, replace_data)

	search_pattern = '(.*)/ruleupdate'
	replace_pattern = '(\s{2})(\d+)(\s{2})(\d+)(\s{2})'
	time_list = ruleupdate_time.split(':')
	replace_data = '  {minute}  {hour}  '.format(minute=int(time_list[1]), hour=int(time_list[0]))
	update_file(file_path, search_pattern, replace_pattern, replace_data)


def update_warning_file(level):
	file_path = current_app.config.get('BIGEYE_CFG_FILE')
	search_pattern = 'alertlevel = (\d+)'
	replace_pattern = '(\d+)'
	replace_data = level

	update_file(file_path, search_pattern, replace_pattern, replace_data)


def save_warning(warning_setting, request):
	if request.method == 'POST':
		level = request.form['level']
		title = request.form['title']

		error = None
		if not level:
			error = 'level is required.'
		elif not title:
			error = 'title is required.'

		if error is None:
			if warning_setting is not None:
				warning_setting.level = level
				warning_setting.title = title
			else:
				warning_setting = Warning(level, title)
				db.session.add(warning_setting)

			db.session.commit()
			update_warning_file(level)

		flash(error)

	return warning_setting


def save_upgrade(upgrade_setting, request):
	if request.method == 'POST':
		rule_upload_address = request.form['rule_upload_address']
		rule_upgrade_time = request.form['rule_upgrade_time']
		threat_upload_address = request.form['threat_upload_address']
		threat_upgrade_time = request.form['threat_upgrade_time']

		error = None
		if not rule_upload_address:
			error = 'rule upload address is required.'
		elif not rule_upgrade_time:
			error = 'rule upgrade time is required.'
		elif not threat_upload_address:
			error = 'threat upload address is required.'
		elif not threat_upgrade_time:
			error = 'threat upgrade time is required.'

		if error is None:
			if upgrade_setting is not None:
				upgrade_setting.rule_upload_address = rule_upload_address
				upgrade_setting.rule_upgrade_time = rule_upgrade_time
				upgrade_setting.threat_upload_address = threat_upload_address
				upgrade_setting.threat_upgrade_time = threat_upgrade_time
			else:
				upgrade_setting = Upgrade(rule_upload_address, rule_upgrade_time, threat_upload_address,
				                          threat_upgrade_time)
				db.session.add(upgrade_setting)

			db.session.commit()
			update_logupload_file(threat_upload_address)
			update_ruleupdate_file(rule_upload_address)
			update_crontab_file(threat_upgrade_time, rule_upgrade_time)

		flash(error)

	return upgrade_setting


@bp.route('/backup')
@login_required
def backup():
	backup_setting = Backup.query.first()
	return render_template('setting/backup.html', backup_setting=backup_setting)


@bp.route('/backup/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_backup(id):
	backup_setting = Backup.query.filter_by(id=id).first()

	if request.method == 'POST':
		step = request.form['step']

		error = None
		if not step:
			error = 'step is required.'

		if error is None:
			if backup_setting is not None:
				backup_setting.step = step
				db.session.commit()
			else:
				backup_setting = Backup(step)
				db.session.add(backup_setting)

		flash(error)

	return render_template('setting/backup.html', backup_setting=backup_setting)


@bp.route('/backup/create', methods=('GET', 'POST'))
@login_required
def create_backup():
	backup_setting = None

	if request.method == 'POST':
		step = request.form['step']

		error = None
		if not step:
			error = 'step is required.'

		if error is None:
			backup_setting = Backup(step)
			db.session.add(backup_setting)
			db.session.commit()

		flash(error)

	return render_template('setting/backup.html', backup_setting=backup_setting)


@bp.route('/network')
@login_required
def network():
	network_setting = Network.query.first()
	return render_template('setting/network.html', network_setting=network_setting)


def save_network(network_setting, request):
	if request.method == 'POST':
		intranet_segment = request.form['intranet_segment']
		extranet_segment = request.form['extranet_segment']
		intranet_card = request.form['intranet_card']
		extranet_card = request.form['extranet_card']

		error = None
		if not intranet_segment:
			error = 'intranet segment is required.'
		elif not extranet_segment:
			error = 'extranet segment is required.'
		elif not intranet_card:
			error = 'intranet card is required.'
		elif not extranet_card:
			error = 'extranet card is required.'

		if error is None:
			if network_setting is not None:
				network_setting.intranet_segment = intranet_segment
				network_setting.extranet_segment = extranet_segment
				network_setting.intranet_card = intranet_card
				network_setting.extranet_card = extranet_card
			else:
				network_setting = Network(intranet_segment, extranet_segment, intranet_card, extranet_card)
				db.session.add(network_setting)

			db.session.commit()

		flash(error)

	return network_setting


@bp.route('/network/create', methods=('GET', 'POST'))
@login_required
def create_network():
	network_setting = None

	network_setting = save_network(network_setting, request)

	return render_template('setting/network.html', network_setting=network_setting)


@bp.route('/network/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_network(id):
	network_setting = Network.query.filter_by(id=id).first()

	network_setting = save_network(network_setting, request)

	return render_template('setting/network.html', network_setting=network_setting)


def get_process_started_time(proc_name):
	proc_run_days = None
	regex = re.compile("pid=(\d+),\sname=\'" + proc_name + "\',\sstarted=\'(.*)\'")

	for proc in psutil.process_iter():
		process_info = str(proc)
		result = regex.search(process_info)
		if result:
			proc_started_time = parser.parse(result.group(2))
			timedelta = datetime.now() - proc_started_time
			proc_run_days = round(timedelta.days + timedelta.seconds / 3600 / 24, 2)

			# minutes, hours = math.modf(timedelta.seconds / 3600)
			# minutes = int(round(minutes * 60))
			# if days:
			# 	proc_run_time = '{days}天 {hours}小时 {minutes}分钟 '.format(days=timedelta.days, hours=int(hours),
			#                                               minutes=int(minutes))
			# elif hours:
			# 	proc_run_time = '{hours}小时 {minutes}分钟 '.format(hours=int(hours),
			# 	                                minutes=int(minutes))
			# else:
			# 	proc_run_time = '{minutes}分钟 '.format(minutes=int(minutes))

			break

	return None


# return proc_run_days


@bp.route('/process', methods=('GET', 'POST'))
@login_required
def process():
	proc_run_time = {}

	extrannet_proc_name = current_app.config.get('EXTRANNET_PROC_NAME')
	extrannet_proc_run_time = get_process_started_time(extrannet_proc_name)
	proc_run_time.update(extrannet_proc_run_time=extrannet_proc_run_time)

	intrannet_proc_name = current_app.config.get('INTRANNET_PROC_NAME')
	intrannet_proc_run_time = get_process_started_time(intrannet_proc_name)
	proc_run_time.update(intrannet_proc_run_time=intrannet_proc_run_time)

	return render_template('setting/process.html', proc_run_time=proc_run_time)


@bp.route('/process/run', methods=('GET', 'POST'))
@login_required
def run_process():
	if request.method == 'POST':
		process_name = request.form['process_name']
		os.system(process_name)

		return jsonify({'process_name': process_name})

	return jsonify({'process_name': None})


@bp.route('/upgrade/run', methods=('GET', 'POST'))
@login_required
def run_upgrade():
	file_path = current_app.config.get('RULE_UPDATE_FILE')
	os.system(file_path)

	return jsonify({'result': 'success'})


@bp.route('/upgrade/create', methods=('GET', 'POST'))
@login_required
def create_upgrade():
	upgrade_setting = None

	upgrade_setting = save_upgrade(upgrade_setting, request)

	return render_template('setting/upgrade.html', upgrade_setting=upgrade_setting)


@bp.route('/upgrade/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_upgrade(id):
	upgrade_setting = Upgrade.query.filter_by(id=id).first()

	upgrade_setting = save_upgrade(upgrade_setting, request)

	return render_template('setting/upgrade.html', upgrade_setting=upgrade_setting)


@bp.route('/upgrade')
@login_required
def upgrade():
	upgrade_setting = Upgrade.query.first()
	return render_template('setting/upgrade.html', upgrade_setting=upgrade_setting)



@bp.route('/warning')
@login_required
def warning():
	warning_setting = Warning.query.first()
	emails = WarningEmail.query.all()

	return render_template('setting/warning.html', warning_setting=warning_setting, emails=emails)


@bp.route('/warning/create', methods=('GET', 'POST'))
@login_required
def create_warning():
	warning_setting = None

	warning_setting = save_warning(warning_setting, request)

	return render_template('setting/warning.html', warning_setting=warning_setting)


@bp.route('/warning/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_warning(id):
	warning_setting = Warning.query.filter_by(id=id).first()

	warning_setting = save_warning(warning_setting, request)

	return render_template('setting/warning.html', warning_setting=warning_setting)


@bp.route('/email/create', methods=('GET', 'POST'))
@login_required
def create_email():
	warning_email = None
	if request.method == 'POST':
		email = request.form['email']

	error = None
	if not email:
		error = 'email is required.'

	if error is None:
		if warning_email is not None:
			warning_email.email = email
		else:
			warning_email = WarningEmail(email)
			db.session.add(warning_email)
		db.session.commit()

	flash(error)

	return redirect(url_for('setting.warning'))


@bp.route('/email/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete_email(id):
	warning_email = WarningEmail.query.filter_by(id=id).first()
	db.session.delete(warning_email)
	db.session.commit()

	return redirect(url_for('setting.warning'))



