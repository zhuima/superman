# -*- coding: utf-8 -*-
# Author: https://github.com/trytofix/supervisor-easy/blob/master/Server.py


import json
from flask_babel import _
from flask import request, render_template, flash, redirect, url_for, Blueprint, g, current_app, make_response, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from superman.forms import LoginForm, HostGroupForm, HostInfoForm, EditHostGroupForm, EditHostInfoForm, RegistrationForm, ChangePasswordForm
from superman.utils import redirect_back
from superman.models import Admin, HostGroup, HostInfo
from superman.extensions import db
from superman.server import Server

admin_bp = Blueprint('admin', __name__)

@login_required
def common_response(ret):
    return Response(json.dumps({'ret': ret}), content_type='application/json')


@admin_bp.route('/server/<int:hostinfo_id>/status/')
@login_required
def server_status(hostinfo_id):
    hostinfo = HostInfo.query.get_or_404(hostinfo_id)
    rpc_proxy = Server(hostinfo.host, hostinfo.port, hostinfo.username, hostinfo.password)
    page = request.args.get('page', 1, type=int)
    pagination = Admin.query.order_by(Admin.id.desc()).paginate(
        page, per_page=current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE'])
    return render_template('server_status.html', page=page, pagination=pagination, host = hostinfo.host, hostinfo_id=hostinfo.id, apps=rpc_proxy.get_all_process_info())


@admin_bp.route('/server/<int:hostinfo_id>/statusinfo/')
@login_required
def server_statusinfo(hostinfo_id):
    hostinfo = HostInfo.query.get_or_404(hostinfo_id)
    rpc_proxy = Server(hostinfo.host, hostinfo.port, hostinfo.username, hostinfo.password)
    # print(rpc_proxy.get_all_process_info())
    return jsonify({"data": rpc_proxy.get_all_process_info()})


@admin_bp.route('/server/<int:hostinfo_id>/<group>/<appname>/start')
@login_required
def start_app(hostinfo_id, group, appname):
    hostinfo = HostInfo.query.get_or_404(hostinfo_id)
    rpc_proxy = Server(hostinfo.host, hostinfo.port, hostinfo.username, hostinfo.password)
    app_name = '%s:%s' % (group, appname)
    resp = rpc_proxy.start_process(app_name)
    if resp:
    	return common_response(resp)
    else:
    	return common_response("服务已经启动!")



@admin_bp.route('/server/<int:hostinfo_id>/<group>/<appname>/restart')
@login_required
def restart_app(hostinfo_id, group, appname):
	hostinfo = HostInfo.query.get_or_404(hostinfo_id)
	rpc_proxy = Server(hostinfo.host, hostinfo.port, hostinfo.username, hostinfo.password)
	app_name = '%s:%s' % (group, appname)
	resp = rpc_proxy.restart_process(app_name)
	return common_response(resp)


@admin_bp.route('/server/<int:hostinfo_id>/<group>/<appname>/stop')
@login_required
def stop_app(hostinfo_id, group, appname):
	hostinfo = HostInfo.query.get_or_404(hostinfo_id)
	rpc_proxy = Server(hostinfo.host, hostinfo.port, hostinfo.username, hostinfo.password)
	app_name = '%s:%s' % (group, appname)
	resp = rpc_proxy.stop_process(app_name)

	return common_response(resp)


def format_log(log):
    return '<div>%s</div>' % (log,)


@admin_bp.route('/server/<int:hostinfo_id>/<group>/<appname>/tail')
@login_required
def tail_std_log(hostinfo_id, group, appname):
	hostinfo = HostInfo.query.get_or_404(hostinfo_id)
	rpc_proxy = Server(hostinfo.host, hostinfo.port, hostinfo.username, hostinfo.password)
	app_name = '%s:%s' % (group, appname)
	resp = rpc_proxy.tail_log(app_name, format_log)
	return common_response(resp)

