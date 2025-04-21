from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models import db, Notice
from datetime import datetime

notice_service = Blueprint('notice_service', __name__, url_prefix='/notices')

@notice_service.route('/admin/add', methods=['GET', 'POST'])
def add_notice():
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if title and content:
            new_notice = Notice(title=title, content=content, timestamp=datetime.utcnow())
            db.session.add(new_notice)
            db.session.commit()
            flash('Notice added successfully!', 'success')
            return redirect(url_for('dashboard_service.admin_dashboard'))
        else:
            flash('Title and content are required!', 'error')

    return render_template('add_notice.html')

@notice_service.route('/view')
def view_notices():
    # Fetch all notices in descending order of timestamp (latest first)
    notices = Notice.query.order_by(Notice.timestamp.desc()).all()

    # Filter out any None values (if they exist)
    notices = [notice for notice in notices if notice is not None]

    return render_template('view_notices.html', notices=notices)