from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.event import Event
from app.models.memorial import Memorial
from app import db
from datetime import datetime

bp = Blueprint('event', __name__)

@bp.route('/memorial/<int:memorial_id>/events')
def list_events(memorial_id):
    memorial = Memorial.query.get_or_404(memorial_id)
    if not memorial.is_public and (not current_user.is_authenticated or current_user.id != memorial.creator_id):
        return render_template('memorial/private.html')
    return render_template('event/list.html', memorial=memorial, now=datetime.utcnow())

@bp.route('/memorial/<int:memorial_id>/events/create', methods=['GET', 'POST'])
@login_required
def create_event(memorial_id):
    memorial = Memorial.query.get_or_404(memorial_id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to create events')
        return redirect(url_for('memorial.view', id=memorial_id))
        
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            date=datetime.strptime(f"{request.form.get('date')} {request.form.get('time')}", '%Y-%m-%d %H:%M'),
            location=request.form.get('location'),
            is_online=bool(request.form.get('is_online')),
            online_link=request.form.get('online_link'),
            memorial_id=memorial_id,
            creator_id=current_user.id
        )
        
        if request.form.get('end_date'):
            event.end_date = datetime.strptime(
                f"{request.form.get('end_date')} {request.form.get('end_time', '23:59')}", 
                '%Y-%m-%d %H:%M'
            )
            
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully')
        return redirect(url_for('event.view_event', memorial_id=memorial_id, event_id=event.id))
        
    return render_template('event/create.html', memorial=memorial)

@bp.route('/memorial/<int:memorial_id>/events/<int:event_id>')
def view_event(memorial_id, event_id):
    event = Event.query.get_or_404(event_id)
    if event.memorial_id != memorial_id:
        abort(404)
    if not event.memorial.is_public and (not current_user.is_authenticated or current_user.id != event.memorial.creator_id):
        return render_template('memorial/private.html')
    return render_template('event/view.html', event=event, now=datetime.utcnow())

@bp.route('/memorial/<int:memorial_id>/events/<int:event_id>/rsvp', methods=['POST'])
@login_required
def rsvp(memorial_id, event_id):
    event = Event.query.get_or_404(event_id)
    if event.memorial_id != memorial_id:
        abort(404)
        
    status = request.form.get('status')
    if status not in ['attending', 'declined']:
        abort(400)
        
    if status == 'attending':
        if current_user not in event.attendees:
            event.attendees.append(current_user)
    else:
        if current_user in event.attendees:
            event.attendees.remove(current_user)
            
    db.session.commit()
    flash(f'RSVP updated to {status}')
    return redirect(url_for('event.view_event', memorial_id=memorial_id, event_id=event_id))

@bp.route('/memorial/<int:memorial_id>/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(memorial_id, event_id):
    event = Event.query.get_or_404(event_id)
    if event.memorial_id != memorial_id:
        abort(404)
    if current_user.id != event.creator_id:
        flash('You do not have permission to edit this event')
        return redirect(url_for('event.view_event', memorial_id=memorial_id, event_id=event_id))
        
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.date = datetime.strptime(f"{request.form.get('date')} {request.form.get('time')}", '%Y-%m-%d %H:%M')
        event.location = request.form.get('location')
        event.is_online = bool(request.form.get('is_online'))
        event.online_link = request.form.get('online_link')
        
        if request.form.get('end_date'):
            event.end_date = datetime.strptime(
                f"{request.form.get('end_date')} {request.form.get('end_time', '23:59')}", 
                '%Y-%m-%d %H:%M'
            )
        else:
            event.end_date = None
            
        db.session.commit()
        flash('Event updated successfully')
        return redirect(url_for('event.view_event', memorial_id=memorial_id, event_id=event_id))
        
    return render_template('event/edit.html', event=event)

@bp.route('/memorial/<int:memorial_id>/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(memorial_id, event_id):
    event = Event.query.get_or_404(event_id)
    if event.memorial_id != memorial_id:
        abort(404)
    if current_user.id != event.creator_id:
        flash('You do not have permission to delete this event')
        return redirect(url_for('event.view_event', memorial_id=memorial_id, event_id=event_id))
        
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully')
    return redirect(url_for('event.list_events', memorial_id=memorial_id)) 