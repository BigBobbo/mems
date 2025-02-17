from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app.models.memorial import Memorial
from app.models.tribute import Tribute
from app.models.photo import Photo
from app import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app.utils.qr import generate_memorial_qr
from app.models.theme import Theme
from app.utils.storage import S3Storage
from app.utils.db_monitor import monitor_db
from slugify import slugify

bp = Blueprint('memorial', __name__)

storage = S3Storage()

@bp.route('/')
def index():
    memorials = Memorial.query.filter_by(is_public=True).all()
    return render_template('memorial/index.html', memorials=memorials)

@bp.route('/memorial/<int:id>')
def view(id):
    memorial = Memorial.query.get_or_404(id)
    
    if not memorial.is_public:
        if not current_user.is_authenticated:
            abort(403)
        if current_user.id != memorial.creator_id:
            abort(403)
    
    # Use theme-specific template if available, otherwise use classic theme
    if memorial.theme:
        print(f"Using theme template: {memorial.theme.template_path}")
        template = memorial.theme.template_path
    else:
        print("Using default classic theme")
        template = 'themes/classic/memorial.html'
        
    return render_template(template, 
                         memorial=memorial, 
                         now=datetime.utcnow())

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        death_date = request.form.get('death_date')
        
        if not name:
            flash('Name is required')
            return render_template('memorial/create.html')
            
        if not birth_date:
            flash('Birth date is required')
            return render_template('memorial/create.html')
            
        if not death_date:
            flash('Death date is required')
            return render_template('memorial/create.html')
            
        try:
            memorial = Memorial(
                name=name,
                birth_date=datetime.strptime(birth_date, '%Y-%m-%d'),
                death_date=datetime.strptime(death_date, '%Y-%m-%d'),
                biography=request.form.get('biography'),
                is_public=bool(request.form.get('is_public')),
                creator_id=current_user.id
            )
            
            # Handle custom URL
            custom_url = request.form.get('custom_url')
            if custom_url:
                if Memorial.query.filter_by(custom_url=slugify(custom_url)).first():
                    flash('Custom URL already taken')
                    return render_template('memorial/create.html')
                memorial.set_custom_url(custom_url)
            else:
                memorial.set_custom_url()
            
            db.session.add(memorial)
            db.session.commit()
            flash('Memorial created successfully')
            return redirect(url_for('memorial.view', id=memorial.id))
            
        except Exception as e:
            current_app.logger.error(f"Error creating memorial: {e}")
            db.session.rollback()
            flash('Error creating memorial')
            return render_template('memorial/create.html')
            
    return render_template('memorial/create.html')

@bp.route('/memorial/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@monitor_db
def edit(id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to edit this memorial')
        return redirect(url_for('memorial.view', id=id))
        
    if request.method == 'POST':
        custom_url = request.form.get('custom_url')
        if custom_url:
            slugified_url = slugify(custom_url)
            existing = Memorial.query.filter_by(custom_url=slugified_url).first()
            if existing and existing.id != memorial.id:
                flash('Custom URL already taken')
                return render_template('memorial/edit.html', memorial=memorial)
            memorial.set_custom_url(custom_url)
        
        memorial.name = request.form.get('name')
        memorial.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d')
        memorial.death_date = datetime.strptime(request.form.get('death_date'), '%Y-%m-%d')
        memorial.biography = request.form.get('biography')
        memorial.is_public = bool(request.form.get('is_public'))
        memorial.theme_id = request.form.get('theme_id', type=int)
        memorial.layout = request.form.get('layout', 'standard')
        
        try:
            db.session.commit()
            flash('Memorial updated successfully')
            return redirect(url_for('memorial.view', id=id))
        except Exception as e:
            current_app.logger.error(f"Error updating memorial: {e}")
            db.session.rollback()
            flash('Error updating memorial')
            
    return render_template('memorial/edit.html', 
                         memorial=memorial,
                         themes=Theme.query.filter_by(is_active=True).all())

@bp.route('/memorial/<int:id>/tribute', methods=['POST'])
@login_required
def add_tribute(id):
    memorial = Memorial.query.get_or_404(id)
    content = request.form.get('content')
    
    if not content:
        flash('Tribute content is required')
        return redirect(url_for('memorial.view', id=id))
        
    tribute = Tribute(
        content=content,
        author_id=current_user.id,
        memorial_id=memorial.id,
        is_approved=current_user.id == memorial.creator_id  # Auto-approve if creator
    )
    
    db.session.add(tribute)
    db.session.commit()
    
    if tribute.is_approved:
        flash('Your tribute has been posted')
    else:
        flash('Your tribute has been submitted for approval')
    
    return redirect(url_for('memorial.view', id=id))

@bp.route('/memorial/<int:id>/tributes')
@login_required
def manage_tributes(id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to manage tributes')
        return redirect(url_for('memorial.view', id=id))
        
    pending_tributes = memorial.tributes.filter_by(is_approved=False).all()
    return render_template('memorial/manage_tributes.html', 
                         memorial=memorial, 
                         pending_tributes=pending_tributes)

@bp.route('/memorial/tribute/<int:tribute_id>/approve', methods=['POST'])
@login_required
def approve_tribute(tribute_id):
    tribute = Tribute.query.get_or_404(tribute_id)
    if current_user.id != tribute.memorial.creator_id:
        flash('You do not have permission to approve tributes')
        return redirect(url_for('memorial.view', id=tribute.memorial_id))
        
    tribute.is_approved = True
    db.session.commit()
    flash('Tribute approved')
    return redirect(url_for('memorial.manage_tributes', id=tribute.memorial_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_photo(file, memorial_id):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to prevent duplicates
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{int(datetime.utcnow().timestamp())}{ext}"
        
        # Create memorial-specific directory if it doesn't exist
        photo_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(memorial_id))
        os.makedirs(photo_dir, exist_ok=True)
        
        file_path = os.path.join(photo_dir, filename)
        file.save(file_path)
        return filename
    return None

@bp.route('/memorial/<int:id>/photos', methods=['GET', 'POST'])
@login_required
def manage_photos(id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to manage photos')
        return redirect(url_for('memorial.view', id=id))
    
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No photo uploaded')
            return redirect(request.url)
            
        file = request.files['photo']
        if file.filename == '':
            flash('No photo selected')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                filename = storage.upload_file(file, id, file.filename)
                if filename:
                    photo = Photo(
                        filename=filename,
                        caption=request.form.get('caption'),
                        memorial_id=id,
                        is_profile=request.form.get('is_profile') == 'true',
                        date_taken=datetime.strptime(request.form.get('date_taken'), '%Y-%m-%d') if request.form.get('date_taken') else None
                    )
                    db.session.add(photo)
                    db.session.commit()
                    flash('Photo uploaded successfully')
                else:
                    flash('Error uploading photo')
            except Exception as e:
                current_app.logger.error(f"Upload error: {e}")
                flash('Error uploading photo')
                
    return render_template('memorial/manage_photos.html', 
                         memorial=memorial,
                         Photo=Photo)

@bp.route('/memorial/<int:id>/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(id, photo_id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to delete photos')
        return redirect(url_for('memorial.view', id=id))
        
    photo = Photo.query.get_or_404(photo_id)
    if photo.memorial_id != id:
        abort(404)
        
    # Delete from S3
    if storage.delete_file(id, photo.filename):
        db.session.delete(photo)
        db.session.commit()
        flash('Photo deleted')
    else:
        flash('Error deleting photo', 'error')
        
    return redirect(url_for('memorial.manage_photos', id=id))

@bp.route('/memorial/<int:id>/photo/<int:photo_id>/set-profile', methods=['POST'])
@login_required
def set_profile_photo(id, photo_id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to manage photos')
        return redirect(url_for('memorial.view', id=id))
        
    # Reset all profile photos
    Photo.query.filter_by(memorial_id=id, is_profile=True).update({'is_profile': False})
    
    # Set new profile photo
    photo = Photo.query.get_or_404(photo_id)
    if photo.memorial_id != id:
        abort(404)
        
    photo.is_profile = True
    db.session.commit()
    flash('Profile photo updated')
    return redirect(url_for('memorial.manage_photos', id=id))

@bp.route('/memorial/<int:id>/photo/<int:photo_id>/reorder', methods=['POST'])
@login_required
def reorder_photo(id, photo_id):
    if current_user.id != Memorial.query.get_or_404(id).creator_id:
        abort(403)
        
    new_position = request.form.get('position', type=int)
    if new_position is None:
        abort(400)
        
    photo = Photo.query.get_or_404(photo_id)
    if photo.memorial_id != id:
        abort(404)
        
    photo.display_order = new_position
    db.session.commit()
    return {'status': 'success'}

@bp.route('/memorial/<int:id>/gallery')
def view_gallery(id):
    memorial = Memorial.query.get_or_404(id)
    if not memorial.is_public:
        if not current_user.is_authenticated or current_user.id != memorial.creator_id:
            abort(403)  # Return 403 Forbidden instead of rendering private.html
    return render_template('memorial/gallery.html', memorial=memorial, Photo=Photo)

@bp.route('/memorial/<int:id>/qr')
def generate_qr(id):
    memorial = Memorial.query.get_or_404(id)
    if not memorial.is_public:
        if not current_user.is_authenticated or current_user.id != memorial.creator_id:
            abort(403)  # Keep consistent with other routes
        
    url = url_for('memorial.view', id=id, _external=True)
    qr_filename = generate_memorial_qr(id, url)
    
    return render_template('memorial/qr.html', 
                         memorial=memorial,
                         qr_filename=qr_filename)

@bp.route('/memorial/<int:id>/upload', methods=['POST'])
@login_required
def upload_photo(id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        abort(403)
        
    if 'photo' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('memorial.edit', id=id))
        
    file = request.files['photo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('memorial.edit', id=id))
        
    if file and allowed_file(file.filename):
        try:
            filename = storage.upload_file(file, memorial.id, file.filename)
            if filename:
                photo = Photo(
                    filename=filename,
                    memorial_id=memorial.id,
                    is_profile=request.form.get('is_profile', False) == 'true'
                )
                db.session.add(photo)
                db.session.commit()
                flash('Photo uploaded successfully', 'success')
            else:
                flash('Error uploading photo', 'error')
        except Exception as e:
            current_app.logger.error(f"Upload error: {e}")
            flash('Error uploading photo', 'error')
            
    return redirect(url_for('memorial.edit', id=id))

@bp.route('/memorial/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    memorial = Memorial.query.get_or_404(id)
    
    # Check if user is authorized to delete
    if current_user.id != memorial.creator_id:
        abort(403)
        
    try:
        # Delete associated photos from storage
        for photo in memorial.photos:
            storage.delete_file(memorial.id, photo.filename)
            
        # Delete from database
        db.session.delete(memorial)
        db.session.commit()
        
        flash('Memorial has been deleted.', 'success')
        return redirect(url_for('memorial.index'))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting memorial: {e}")
        db.session.rollback()
        flash('An error occurred while deleting the memorial.', 'error')
        return redirect(url_for('memorial.view', id=id))

# Add a route to handle custom URLs
@bp.route('/m/<custom_url>')
def view_by_url(custom_url):
    memorial = Memorial.query.filter_by(custom_url=custom_url).first_or_404()
    if not memorial.is_public and (not current_user.is_authenticated or current_user.id != memorial.creator_id):
        abort(403)
    
    # Use theme-specific template if available, otherwise use classic theme
    if memorial.theme:
        print(f"Using theme template: {memorial.theme.template_path}")
        template = memorial.theme.template_path
    else:
        print("Using default classic theme")
        template = 'themes/classic/memorial.html'
        
    return render_template(template, 
                         memorial=memorial, 
                         now=datetime.utcnow())

# Routes will be added here 