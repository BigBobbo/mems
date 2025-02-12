from app import db

event_attendees = db.Table('event_attendees',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('rsvp_status', db.String(20), default='pending'),  # pending, attending, declined
    db.Column('rsvp_date', db.DateTime, default=db.func.current_timestamp())
) 