from flask import Blueprint, jsonify
from flask import current_app
from flask import db

bp = Blueprint('admin', __name__)

# Routes will be added here 

@bp.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db.session.commit()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        current_app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500 