from app import db
from datetime import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    memorial_id = db.Column(db.Integer, db.ForeignKey('memorial.id'), nullable=False)
    
    def __repr__(self):
        return f'<Event {self.title}>' 