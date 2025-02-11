from app import db
from datetime import datetime

class Tribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    memorial_id = db.Column(db.Integer, db.ForeignKey('memorial.id'), nullable=False)
    
    def __repr__(self):
        return f'<Tribute {self.id}>' 