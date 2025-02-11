from app import db
from datetime import datetime

class Memorial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    biography = db.Column(db.Text)
    custom_url = db.Column(db.String(100), unique=True)
    is_public = db.Column(db.Boolean, default=True)
    access_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    photos = db.relationship('Photo', backref='memorial', lazy='dynamic')
    tributes = db.relationship('Tribute', backref='memorial', lazy='dynamic')
    events = db.relationship('Event', backref='memorial', lazy='dynamic')
    
    def __repr__(self):
        return f'<Memorial {self.name}>' 