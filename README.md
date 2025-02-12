# Memorial Site

A platform for creating and managing digital memorials for loved ones.

## Current Features

### Authentication
- User registration with email and username
- User login/logout functionality
- Password security with hashing
- Session management
- Protected routes with @login_required
- Authorization checks for private content

### Memorial Management
- Create new memorials with:
  - Full name
  - Birth and death dates
  - Biography
  - Custom URL option (with duplicate checking)
  - Public/private visibility setting
- Edit existing memorials
- View public memorials
- Private memorial access control
  - Only authenticated creators can view their private memorials
  - Automatic 403 errors for unauthorized access
- Memorial listing page showing all public memorials

### Tribute System
- Users can submit tributes to memorials
- Automatic approval for memorial creator's tributes
- Moderation system for other tributes
  - Pending tributes queue
  - Approve/reject functionality
  - Creator-only moderation access
- Tribute management interface for memorial owners
- Tribute visibility control based on approval status

### Photo Gallery
- Upload photos with:
  - Captions
  - Date taken (optional)
  - Automatic file naming with timestamps
  - File type validation
  - Secure file handling
- Set profile photos for memorials
- Drag-and-drop photo reordering with SortableJS
- Photo gallery view with lightbox
- Photo management interface:
  - Upload new photos
  - Delete existing photos
  - Set profile photo
  - Reorder photos
  - View photo details
- Memorial-specific photo directories
- Automatic directory creation
- Secure file deletion

### QR Code Integration
- Automatic QR code generation for memorials
- QR codes link to memorial pages
- Memorial-specific QR code storage
- QR code display page
- Access control for private memorial QR codes

### Template System
- Base template with consistent layout
- Error pages (403, etc.)
- Memorial-specific templates:
  - View template
  - Edit template
  - Gallery template
  - Photo management template
  - Tribute management template
  - QR code template

### Security Features
- CSRF protection
- Secure file handling
- Access control checks
- Password hashing
- Protected routes
- Secure session management
- File type validation
- Directory traversal prevention

### UI/UX Features
- Bootstrap 5 responsive design
- Font Awesome icons
- Drag-and-drop interface for photos
- Flash messages for user feedback
- Navigation bar with context-aware links
- Clean URL structure
- Form validation with error messages
- Lightbox for photo viewing
- Sortable photo galleries

### Database Features
- SQLAlchemy ORM integration
- Relationship management:
  - User to Memorials
  - Memorial to Photos
  - Memorial to Tributes
  - User to Tributes
- Cascade deletions
- Foreign key constraints
- Automatic timestamps
- Query optimization

### File Management
- Automatic upload directory creation
- Memorial-specific photo directories
- Secure filename generation
- File type validation
- Automatic file cleanup
- Organized file structure

## Features To Implement

### User Management
- [ ] Password reset functionality
- [ ] Email verification
- [ ] User profile pages
- [ ] Account settings
- [ ] Profile pictures for users

### Memorial Enhancements
- [ ] Search functionality for memorials
- [ ] Memorial categories/tags
- [ ] Featured memorials section
- [ ] Memorial sharing options
- [ ] Memorial visitor statistics

### Events System
- [ ] Create and manage memorial events
- [ ] Event notifications
- [ ] Calendar integration
- [ ] RSVP functionality
- [ ] Event photo galleries

### Social Features
- [ ] Follow/subscribe to memorials
- [ ] Share buttons for social media
- [ ] Comment system for photos
- [ ] Family tree integration
- [ ] Memorial co-administrators

### Content Management
- [ ] Allow for the user to choose different aesthetic themes and layouts
- [ ] Rich text editor for biographies
- [ ] Video upload support
- [ ] Audio memories/stories
- [ ] Document attachments
- [ ] Timeline feature

### Additional Features
- [ ] Mobile app version
- [ ] API development
- [ ] Multiple language support
- [ ] Theme customization
- [ ] Memorial templates
- [ ] Backup system
- [ ] Export functionality
- [ ] Print-to-book option

### Technical Improvements
- [ ] Image optimization
- [ ] Caching system
- [ ] CDN integration
- [ ] Advanced search with filters
- [ ] API rate limiting
- [ ] Automated testing
- [ ] CI/CD pipeline
- [ ] Monitoring and analytics

### Security Enhancements
- [ ] Two-factor authentication
- [ ] OAuth integration
- [ ] Rate limiting
- [ ] GDPR compliance
- [ ] Content moderation tools
- [ ] Audit logging

### Administrative Features
- [ ] Admin dashboard
- [ ] User management interface
- [ ] Content moderation tools
- [ ] Site statistics
- [ ] System logs
- [ ] Backup management

### Automated Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests

### Documentation
- [ ] User documentation
- [ ] Developer documentation
- [ ] API documentation

### Deployment
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Monitoring and logging
- [ ] Performance optimization

### QR Code
- [ ] QR code generation for memorials
- [ ] QR code scanning for memorials

## Technical Stack

- Flask web framework
- SQLAlchemy ORM
- SQLite database
- Bootstrap 5 frontend
- Font Awesome icons
- SortableJS for drag-and-drop
- Flask-Login for authentication
- Werkzeug for security

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/memorial-site.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Initialize database:
```bash
flask db upgrade
```

5. Run tests:
```bash
pytest
```

6. Start development server:
```bash
flask run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 