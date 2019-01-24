# -*- coding: utf-8 -*-
# Author: zhuima


from flask_babel import lazy_gettext as _
from flask import request, render_template, flash, redirect, url_for, Blueprint, g, current_app, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from superman.forms import HostGroupForm, HostInfoForm, EditHostGroupForm, EditHostInfoForm
from superman.utils import redirect_back
from superman.models import Admin, HostGroup, HostInfo
from superman.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    group_num = HostGroup.query.count()
    host_num = HostInfo.query.count()
    user_num = Admin.query.count()
    tasks_num = Admin.query.order_by(Admin.id.desc())

    return render_template('home.html', group_num=group_num, host_num=host_num,  user_num=user_num)


@dashboard_bp.route('/hostgroup/manage')
@login_required
def manage_hostgroup():
    page = request.args.get('page', 1, type=int)
    pagination = HostGroup.query.order_by(HostGroup.timestamp.desc()).paginate(
        page, per_page=current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE'])
    hostgroups = pagination.items
    return render_template('manage_hostgroup.html', page=page, pagination=pagination, hostgroups=hostgroups)


@dashboard_bp.route('/hostgroup/<int:hostgroup_id>/details')
@login_required
def details_hostgroup(hostgroup_id):
    page = request.args.get('page', 1, type=int)
    hostgroup = HostGroup.query.get_or_404(hostgroup_id)

    pagination = HostGroup.query.filter(HostGroup.id==hostgroup_id).paginate(
        page, per_page=current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE'])
    hostgroups = pagination.items
    total_num = len([hostgroup.hostinfos for hostgroup in hostgroups][0])
    return render_template('details_hostgroup.html', page=page, pagination=pagination, total_num=total_num, hostgroups=hostgroups, name=hostgroup.name)



@dashboard_bp.route('/hostgroup/new', methods=['GET', 'POST'])
@login_required
def new_hostgroup():
    form = HostGroupForm()
    if form.validate_on_submit():
        name = form.name.data
        comment = form.comment.data
        hostgroup = HostGroup(name=name, comment=comment)
        # same with:
        # category_id = form.category.data
        # post = Post(title=title, body=body, category_id=category_id)
        db.session.add(hostgroup)
        db.session.commit()
        flash(_('Hostgroup created.'), 'success')
        return redirect(url_for('dashboard.manage_hostgroup', hostgroup_id=hostgroup.id))
    return render_template('new_hostgroup.html', form=form)


@dashboard_bp.route('/hostgroup/<int:hostgroup_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hostgroup(hostgroup_id):
    hostgroup = HostGroup.query.get_or_404(hostgroup_id)
    form = EditHostGroupForm(hostgroup=hostgroup)
    if form.validate_on_submit():
        hostgroup.name = form.name.data
        hostgroup.comment = form.comment.data
        db.session.commit()
        flash(_('HostGroup updated.'), 'success')
        return redirect(url_for('dashboard.manage_hostgroup', hostgroup_id=hostgroup.id))
    form.name.data = hostgroup.name
    form.comment.data = hostgroup.comment 
    return render_template('edit_hostgroup.html', form=form)


@dashboard_bp.route('/hostgroup/<int:hostgroup_id>/delete', methods=['GET', 'DELETE'])
@login_required
def delete_hostgroup(hostgroup_id):
    hostgroup = HostGroup.query.get_or_404(hostgroup_id)
    db.session.delete(hostgroup)
    db.session.commit()
    flash(_('HostGroup deleted.'), 'success')
    # return redirect(url_for('dashboard.manage_hostgroup'))
    return jsonify({'ret': 'success'})




@dashboard_bp.route('/hostinfo/manage')
@login_required
def manage_hostinfo():
    page = request.args.get('page', 1, type=int)
    pagination = HostInfo.query.order_by(HostInfo.timestamp.desc()).paginate(
        page, per_page=current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE'])
    hostinfos = pagination.items
    return render_template('manage_hostinfo.html', page=page, pagination=pagination, hostinfos=hostinfos)



@dashboard_bp.route('/hostinfo/new', methods=['GET', 'POST'])
@login_required
def new_hostinfo():
    form = HostInfoForm()
    if form.validate_on_submit():
        host = form.host.data
        port = form.port.data
        username = form.username.data
        password = form.password.data
        comment = form.comment.data
        hostgroup = HostGroup.query.get(form.hostgroup.data)
        hostinfo = HostInfo(host=host, port=port, username=username, password=password, comment=comment, hostgroup=hostgroup)
        # same with:
        # category_id = form.category.data  
        # post = Post(title=title, body=body, category_id=category_id)
        db.session.add(hostinfo)
        db.session.commit()
        flash(_('HostInfo created.'), 'success')
        return redirect(url_for('dashboard.manage_hostinfo', hostinfo_id=hostinfo.id))
    return render_template('new_hostinfo.html', form=form)


@dashboard_bp.route('/hostinfo/<int:hostinfo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hostinfo(hostinfo_id):
    '''
    1、修复表单自定义验证问题，更新的时候走新的表单   解决了，判断当前值即可  
    2、更新表单的时候把获取到的数据重新塞进去  解决了，这个表单获取的时候获取外键的值即可
    3、password字段不能回显的问题: https://blog.csdn.net/guoqianqian5812/article/details/78569961
    https://stackoverflow.com/questions/21779227/populate-a-passwordfield-in-wtforms
    '''
    hostinfo = HostInfo.query.get_or_404(hostinfo_id)
    form = EditHostInfoForm(hostinfo=hostinfo)
    if form.validate_on_submit():
        hostinfo.host = form.host.data
        hostinfo.port = form.port.data
        hostinfo.username = form.username.data
        hostinfo.password = form.password.data
        hostinfo.comment = form.comment.data
        hostgroup = HostGroup.query.get(form.hostgroup.data)
        hostinfo.hostgroup = hostgroup
        db.session.commit()
        flash(_('HostInfo updated.'), 'info')
        return redirect(url_for('dashboard.manage_hostinfo', hostinfo_id=hostinfo.id))
    form.host.data = hostinfo.host
    form.port.data = hostinfo.port
    form.username.data = hostinfo.username
    form.password.data = hostinfo.password
    form.comment.data = hostinfo.comment
    form.hostgroup.data = hostinfo.group_id 
    return render_template('edit_hostinfo.html', form=form, hostinfo=hostinfo)



@dashboard_bp.route('/hostinfo/<int:hostinfo_id>/delete', methods=['GET', 'DELETE'])
# @login_required
def delete_hostinfo(hostinfo_id):
    hostinfo = HostInfo.query.get_or_404(hostinfo_id)
    db.session.delete(hostinfo)
    db.session.commit()
    flash(_('HostInfo deleted.'), 'success')
    # return redirect(url_for('dashboard.manage_hostinfo'))
    return jsonify({'ret': 'success'})



@dashboard_bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    page = request.args.get('page', 1, type=int)
    pagination = HostInfo.query.order_by(HostInfo.timestamp.desc()).paginate(
        page, per_page=current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE'])
    hostinfos = pagination.items
    # print(hostinfos)
    return render_template('tasks.html', page=page, pagination=pagination, hostinfos=hostinfos)


@dashboard_bp.route('/tasksinfo', methods=['GET', 'POST'])
@login_required
def tasksinfo():
    hgs = HostGroup.query.order_by(HostGroup.timestamp.desc())
    resp = [{"name": hg.name, "open": True, "children": [{"name": h.host, "id": h.id } for h in hg.hostinfos ] } for hg in hgs]
    # return jsonify({'data': hostinfos})
    # return make_response(str(resp))
    # print({"data": resp})
    return jsonify({"data": resp})



@dashboard_bp.route('/search')
@login_required
def search():
    q = request.args.get('q', '')
    if q == '':
        flash(_('Enter keyword about Group, Host or User.'), 'error')
        return redirect_back()

    category = request.args.get('category', 'hostgroup')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE']
    if category == 'user':
        pagination = Admin.query.whooshee_search(q).paginate(page, per_page)
    elif category == 'hostgroup':
        pagination = HostGroup.query.whooshee_search(q).paginate(page, per_page)
    else:
        pagination = HostInfo.query.whooshee_search(q).paginate(page, per_page)
    results = pagination.items
    # print(results)
    return render_template('search.html', q=q, page=page, results=results, pagination=pagination, category=category)
