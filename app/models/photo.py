from app import db
from datetime import datetime
import os

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    date_taken = db.Column(db.Date)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_profile = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    
    # Foreign Key
    memorial_id = db.Column(db.Integer, db.ForeignKey('memorial.id'), nullable=False)
    
    def __repr__(self):
        return f'<Photo {self.filename}>' 

    @staticmethod
    def reorder_photos(memorial_id):
        photos = Photo.query.filter_by(memorial_id=memorial_id).order_by(Photo.display_order).all()
        for i, photo in enumerate(photos):
            photo.display_order = i 