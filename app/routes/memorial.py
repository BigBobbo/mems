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

bp = Blueprint('memorial', __name__)

@bp.route('/')
def index():
    memorials = Memorial.query.filter_by(is_public=True).all()
    return render_template('memorial/index.html', memorials=memorials)

@bp.route('/memorial/<int:id>')
def view(id):
    memorial = Memorial.query.get_or_404(id)
    if not memorial.is_public:
        return render_template('memorial/private.html')
    return render_template('memorial/view.html', memorial=memorial, now=datetime.utcnow())

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        memorial = Memorial(
            name=request.form.get('name'),
            birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d'),
            death_date=datetime.strptime(request.form.get('death_date'), '%Y-%m-%d'),
            biography=request.form.get('biography'),
            is_public=bool(request.form.get('is_public')),
            creator_id=current_user.id
        )
        
        custom_url = request.form.get('custom_url')
        if custom_url:
            if Memorial.query.filter_by(custom_url=custom_url).first():
                flash('Custom URL already taken')
                return render_template('memorial/create.html')
            memorial.custom_url = custom_url
            
        db.session.add(memorial)
        db.session.commit()
        flash('Memorial created successfully')
        return redirect(url_for('memorial.view', id=memorial.id))
        
    return render_template('memorial/create.html')

@bp.route('/memorial/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    memorial = Memorial.query.get_or_404(id)
    if current_user.id != memorial.creator_id:
        flash('You do not have permission to edit this memorial')
        return redirect(url_for('memorial.view', id=id))
        
    if request.method == 'POST':
        memorial.name = request.form.get('name')
        memorial.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d')
        memorial.death_date = datetime.strptime(request.form.get('death_date'), '%Y-%m-%d')
        memorial.biography = request.form.get('biography')
        memorial.is_public = bool(request.form.get('is_public'))
        
        custom_url = request.form.get('custom_url')
        if custom_url and custom_url != memorial.custom_url:
            if Memorial.query.filter_by(custom_url=custom_url).first():
                flash('Custom URL already taken')
                return render_template('memorial/edit.html', memorial=memorial)
            memorial.custom_url = custom_url
            
        db.session.commit()
        flash('Memorial updated successfully')
        return redirect(url_for('memorial.view', id=id))
        
    return render_template('memorial/edit.html', memorial=memorial)

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
            
        filename = save_photo(file, id)
        if filename:
            photo = Photo(
                filename=filename,
                caption=request.form.get('caption'),
                memorial_id=id,
                date_taken=datetime.strptime(request.form.get('date_taken'), '%Y-%m-%d') if request.form.get('date_taken') else None
            )
            db.session.add(photo)
            db.session.commit()
            flash('Photo uploaded successfully')
        else:
            flash('Invalid file type')
            
    return render_template('memorial/manage_photos.html', memorial=memorial, Photo=Photo)

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
        
    # Delete file from filesystem
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                            str(id), photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted')
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
        return render_template('memorial/private.html')
    return render_template('memorial/gallery.html', memorial=memorial, Photo=Photo)

@bp.route('/memorial/<int:id>/qr')
def generate_qr(id):
    memorial = Memorial.query.get_or_404(id)
    if not memorial.is_public:
        abort(403)
        
    url = url_for('memorial.view', id=id, _external=True)
    qr_filename = generate_memorial_qr(id, url)
    
    return render_template('memorial/qr.html', 
                         memorial=memorial,
                         qr_filename=qr_filename)

# Routes will be added here 