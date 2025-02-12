from app import db
from app.models import User, Memorial, Tribute, Photo, Event
from app.models.theme import Theme

def init_themes():
    """Initialize default themes if they don't exist"""
    print("Initializing themes...")
    
    default_themes = [
        {
            'name': 'Classic',
            'description': 'Traditional, elegant design with serif fonts',
            'template_path': 'themes/classic/memorial.html',
            'css_path': 'themes/classic.css',
            'is_active': True
        },
        {
            'name': 'Modern',
            'description': 'Clean, contemporary layout with sans-serif fonts',
            'template_path': 'themes/modern/memorial.html',
            'css_path': 'themes/modern.css',
            'is_active': True
        }
    ]

    # Delete existing themes first
    Theme.query.delete()
    
    for theme_data in default_themes:
        print(f"Adding theme: {theme_data['name']} with template: {theme_data['template_path']}")
        theme = Theme(**theme_data)
        db.session.add(theme)
    
    try:
        db.session.commit()
        print("Themes initialized successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing themes: {e}")

def init_db():
    """Initialize database with required data"""
    # Create all tables first
    db.create_all()
    
    # Then initialize data
    init_themes()
    # Add other initialization functions here 