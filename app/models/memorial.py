from app import db
from datetime import datetime
from slugify import slugify

class Memorial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    biography = db.Column(db.Text)
    custom_url = db.Column(db.String(100), unique=True, index=True)
    is_public = db.Column(db.Boolean, default=True)
    access_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))
    layout = db.Column(db.String(32), default='standard')  # standard, compact, full-width, etc.
    
    # Relationships
    photos = db.relationship('Photo', backref='memorial', lazy='dynamic')
    tributes = db.relationship('Tribute', backref='memorial', lazy='dynamic')
    events = db.relationship('Event', backref='memorial', lazy='dynamic')
    
    def __repr__(self):
        return f'<Memorial {self.name}>'
    
    @staticmethod
    def generate_unique_url(name):
        """Generate a unique URL slug from the name"""
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        
        while Memorial.query.filter_by(custom_url=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug
    
    def set_custom_url(self, custom_url=None):
        """Set a custom URL, or generate one from the name"""
        if custom_url:
            self.custom_url = slugify(custom_url)
        else:
            self.custom_url = self.generate_unique_url(self.name) 