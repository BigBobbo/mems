from app import db
from datetime import datetime

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    template_path = db.Column(db.String(128), nullable=False)
    css_path = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with memorials using this theme
    memorials = db.relationship('Memorial', backref='theme', lazy='dynamic') 