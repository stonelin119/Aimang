from datetime import datetime, timedelta

from flask import (
	current_app, Blueprint, render_template
)

from ... import db
from .auth import login_required
from ..models.setting import Network, NetworkTypeEnum
from pyecharts import Line, Bar, Pie

import pandas
import json
import urllib.request


bp = Blueprint('log', __name__, url_prefix='/log')


def convert_ip_to_country(src):
	url = current_app.config.get('CONVERT_IP_URL').format(ip=src)
	response = urllib.request.urlopen(url)
	response = json.load(response)
	country = response['data']['country']

	return country


def build_df_top10_grouped_by_src_dst(df):
	country_column = []
	grouped_df = df.groupby(['src', 'dst']).agg({'msg': 'count'})\
		.sort_values(by='msg').tail(10)

	for (src, dst) in grouped_df.index:
		country_column.append(convert_ip_to_country(src))

	grouped_df['country'] = country_column
	return grouped_df


def convert_timestamp_to_hour(log):
	log_timestamp = log.timestamp
	# log_timestamp_hour = log_timestamp.strftime('%Y-%m-%d %H:00:00')
	log_timestamp_hour = log_timestamp.strftime('%H:00')

	return log_timestamp_hour


def convert_timestamp_to_day(log):
	log_timestamp = log.timestamp
	log_timestamp_day = log_timestamp.strftime('%Y-%m-%d')

	return log_timestamp_day


def load_24hour_log():
	query_sql = 'SELECT msg,dst,dstport,src,srcport,priority,timestamp FROM log'
	df = pandas.read_sql(query_sql, db.session.bind)

	start_time = datetime.now() + timedelta(hours=-24)
	df = df[df.timestamp > start_time]

	if not df.empty:
		df['timestamp_hour'] = df.apply(convert_timestamp_to_hour, axis=1)

	return df


def mark_dst_network_type(log, intranet_segment):
	network_type = NetworkTypeEnum.intranet if (log.dst.find(intranet_segment) == 0) else NetworkTypeEnum.extranet

	return network_type


def load_7day_log():
	query_sql = 'SELECT msg,dst,dstport,src,srcport,priority,timestamp FROM log'
	df = pandas.read_sql(query_sql, db.session.bind)

	start_time = datetime.now() + timedelta(days=-7)
	df = df[df.timestamp > start_time]

	if not df.empty:
		df['timestamp_day'] = df.apply(convert_timestamp_to_day, axis=1)

		network_setting = Network.query.first()
		df['network_type'] = df.apply(mark_dst_network_type, axis=1, args=(network_setting.intranet_segment,))

	return df


def build_top10_risk_diagram(df, logs):
	df_empty = None
	df_top10_high_risk_grouped_by_hour = None
	df_top10_low_risk_grouped_by_hour = None

	if not df.empty:
		df_top10_high_risk_grouped_by_hour = df[df.priority.isin([0, 1])].groupby('timestamp_hour').agg({'msg': 'count'}).sort_values(by='msg').tail(10)
		df_top10_low_risk_grouped_by_hour = df[df.priority == 2].groupby('timestamp_hour').agg({'msg': 'count'}).sort_values(by='msg').tail(10)

		start_time = datetime.now() + timedelta(hours=-24)
		dates = [(start_time + timedelta(hours=i)).strftime('%H:00') for i in range(0, 24)]
		# dates = [(start_time + timedelta(hours=i)).strftime('%Y-%m-%d %H:00:00') for i in range(0, 23)]
		df_empty = pandas.DataFrame({'timestamp_hour': dates, 'msg': 0})
		df_top10_high_risk_grouped_by_hour = pandas.merge(df_empty, df_top10_high_risk_grouped_by_hour, how='left', on='timestamp_hour')
		df_top10_high_risk_grouped_by_hour = df_top10_high_risk_grouped_by_hour.fillna(value=0)
		df_top10_low_risk_grouped_by_hour = pandas.merge(df_empty, df_top10_low_risk_grouped_by_hour, how='left', on='timestamp_hour')
		df_top10_low_risk_grouped_by_hour = df_top10_low_risk_grouped_by_hour.fillna(value=0)

	attr = list(df_empty['timestamp_hour']) if df_empty is not None else {}
	v1 = list(df_top10_high_risk_grouped_by_hour['msg_y']) if df_top10_high_risk_grouped_by_hour is not None else {}
	v2 = list(df_top10_low_risk_grouped_by_hour['msg_y']) if df_top10_low_risk_grouped_by_hour is not None else {}

	line = Line()
	line.add("高威胁", attr, v1)
	line.add("中低威胁", attr, v2)
	logs.update(top10_risk_diagram=line.render_embed())
	logs.update(echart_line_script_list=line.get_js_dependencies())


def build_top10_dst_diagram(df, logs):
	df_top10_grouped_by_dst = None

	if not df.empty:
		df_top10_grouped_by_dst = df.groupby('dst').agg({'msg': 'count'})\
			.sort_values(by='msg').tail(10)

	attr = list(df_top10_grouped_by_dst.index) if df_top10_grouped_by_dst is not None else {}
	v = list(df_top10_grouped_by_dst['msg']) if df_top10_grouped_by_dst is not None else {}
	bar = Bar()
	bar.add("DST", attr, v)

	logs.update(top10_dst_diagram=bar.render_embed())
	logs.update(echart_bar_script_list=bar.get_js_dependencies())

def build_top10_dst_port_diagram(df, logs):
	df_top10_grouped_by_dst_port = None

	if not df.empty:
		df_top10_grouped_by_dst_port = df.groupby('dstport').agg({'msg': 'count'})\
			.sort_values(by='msg').tail(10)

	attr = list(df_top10_grouped_by_dst_port.index) if df_top10_grouped_by_dst_port is not None else {}
	v = list(df_top10_grouped_by_dst_port['msg']) if df_top10_grouped_by_dst_port is not None else {}
	pie = Pie()
	pie.add("DST Port", attr, v)

	logs.update(top10_dst_port_diagram=pie.render_embed())
	logs.update(echart_pie_script_list=pie.get_js_dependencies())


def build_count_perday(df, logs):
	df_empty = None
	df_count_perday = None

	if not df.empty:
		df_count_perday = df.groupby('timestamp_day').agg({'msg': 'count'}).sort_values(by='msg').tail(10)
		start_day = datetime.now() + timedelta(days=-7)
		dates = [(start_day + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 7)]
		df_empty = pandas.DataFrame({'timestamp_day': dates, 'msg': 0})
		df_count_perday = pandas.merge(df_empty, df_count_perday, how='left', on='timestamp_day')
		df_count_perday = df_count_perday.fillna(value=0)

	attr = list(df_empty['timestamp_day']) if df_empty is not None else {}
	v = list(df_count_perday['msg_y']) if df_count_perday is not None else {}

	line = Line()
	line.add("威胁检测", attr, v)

	logs.update(count_perday=line.render_embed())
	logs.update(echart_line_script_list=line.get_js_dependencies())


@bp.route('/')
@login_required
def index():
	df = load_24hour_log()

	logs = {}
	# if not df.empty:
	logs.update(echart_host='https://pyecharts.github.io/assets/js')

	# The count of msg containing the word of 'DOS'
	df_dos_count = df[df.msg.str.contains("DOS")].agg({'msg': 'count'})['msg']
	logs.update(df_DOS_count=df_dos_count)

	# The count of msg containing the word of 'CnC'
	df_cnc_count = df[df.msg.str.contains("CnC")].agg({'msg': 'count'})['msg']
	logs.update(df_CnC_count=df_cnc_count)

	# The count of msg containing the word of 'Malware'
	df_malware_count = df[df.msg.str.contains("Malware")].agg({'msg': 'count'})['msg']
	logs.update(df_Malware_count=df_malware_count)

	# Top 10 count of per-hour logs with priority is 0 or 1
	df_high_risk_count = df[df.priority.isin([0, 1])].agg({'msg': 'count'})['msg']
	logs.update(df_high_risk_count=df_high_risk_count)

	# Top 10 count of per-hour logs with priority is 0 or 1
	build_top10_risk_diagram(df, logs)

	# Top 10 count of DST
	build_top10_dst_diagram(df, logs)

	# Top 10 count of DST Port
	build_top10_dst_port_diagram(df, logs)

	# Top 10 count of SRC & DST
	df_top10_grouped_by_src_dst = build_df_top10_grouped_by_src_dst(df)
	logs.update(df_top10_grouped_by_src_dst=df_top10_grouped_by_src_dst)

	return render_template('log/index.html', logs=logs)


@bp.route('/threat')
@login_required
def threat():
	df = load_7day_log()

	logs = {}
	if not df.empty:
		logs.update(echart_host='https://pyecharts.github.io/assets/js')

		# The count of logs per-day
		build_count_perday(df, logs)

		# The latest 10 logs
		df_latest_10 = df.sort_values(by='timestamp_day').tail(10)
		logs.update(df_latest_10=df_latest_10)

		# The extranet threat statics
		df_extranet_high_threat = df[(df.network_type == NetworkTypeEnum.extranet) & (df.priority.isin([0, 1]))]\
		    .groupby('dst').agg({'msg': 'count'})
		df_extranet_low_threat = df[(df.network_type == NetworkTypeEnum.extranet) & (df.priority == 2)]\
		    .groupby('dst').agg({'msg': 'count'})
		df_extranet_threat = pandas.merge(df_extranet_high_threat, df_extranet_low_threat, how='outer', on=['dst'])
		df_extranet_threat = df_extranet_threat.fillna(value=0)
		df_extranet_threat['sum'] = df_extranet_threat.apply(lambda x: x.msg_x + x.msg_y, axis=1)
		df_extranet_threat.sort_values(by='sum').tail(5)
		logs.update(df_extranet_threat=df_extranet_threat)

		# The intranet threat statics
		df_intranet_high_threat = df[(df.network_type == NetworkTypeEnum.intranet) & (df.priority.isin([0, 1]))]\
			.groupby('dst').agg({'msg': 'count'})
		df_intranet_low_threat = df[(df.network_type == NetworkTypeEnum.intranet) & (df.priority == 2)]\
			.groupby('dst').agg({'msg': 'count'})
		df_intranet_threat = pandas.merge(df_intranet_high_threat, df_intranet_low_threat, how='outer', on=['dst'])
		df_intranet_threat = df_intranet_threat.fillna(value=0)
		df_intranet_threat['sum'] = df_intranet_threat.apply(lambda x: x.msg_x + x.msg_y, axis=1)
		df_intranet_threat.sort_values(by='sum').tail(5)
		logs.update(df_intranet_threat=df_intranet_threat)

	return render_template('log/threat.html', logs=logs)

