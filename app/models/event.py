from app import db
from datetime import datetime
from app.models.event_attendee import event_attendees

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    is_online = db.Column(db.Boolean, default=False)
    online_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    memorial_id = db.Column(db.Integer, db.ForeignKey('memorial.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('created_events', lazy='dynamic'))
    attendees = db.relationship('User', secondary=event_attendees,
                              backref=db.backref('events_attending', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Event {self.title}>' 