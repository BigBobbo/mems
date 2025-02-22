import boto3
import os
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from flask import current_app, url_for
import logging

class S3Storage:
    def __init__(self):
        self.use_local = True  # Default to local storage
        self.s3 = None
        self.bucket = None
        
    def init_app(self, app):
        """Initialize storage with Flask app context"""
        # Force S3 in production
        self.use_local = app.config.get('USE_LOCAL_STORAGE', False)
        if os.environ.get('RENDER'):
            self.use_local = False
            
        if not self.use_local:
            # Verify AWS credentials are present
            required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BUCKET_NAME']
            missing_vars = [var for var in required_vars if not app.config.get(var)]
            
            if missing_vars:
                app.logger.error(f"Missing required AWS credentials: {', '.join(missing_vars)}")
                raise RuntimeError(f"Missing required AWS credentials: {', '.join(missing_vars)}")
                
            try:
                self.s3 = boto3.client(
                    's3',
                    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                    region_name=app.config['AWS_REGION']
                )
                # Test the connection
                self.s3.list_buckets()
                self.bucket = app.config['AWS_BUCKET_NAME']
                app.logger.info("Successfully connected to AWS S3")
            except Exception as e:
                app.logger.error(f"Failed to initialize S3 connection: {e}")
                raise RuntimeError(f"Failed to initialize S3: {e}")
        
        # Create local upload directory for development
        if self.use_local:
            app.logger.warning("Using local storage (development mode)")
            upload_dir = os.path.join(app.static_folder, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

    def upload_file(self, file_obj, memorial_id, filename):
        """Upload a file to S3 or local storage"""
        filename = secure_filename(filename)
        
        if self.use_local:
            try:
                # Save locally
                upload_dir = os.path.join(current_app.static_folder, 'uploads', str(memorial_id))
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file_obj.save(file_path)
                current_app.logger.info(f"File saved locally: {file_path}")
                return filename
            except Exception as e:
                current_app.logger.error(f"Error saving file locally: {e}")
                return None
            
        try:
            key = f'uploads/{memorial_id}/{filename}'
            self.s3.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={
                    'ContentType': file_obj.content_type,
                    'ACL': 'public-read'  # Make sure files are publicly readable
                }
            )
            current_app.logger.info(f"File uploaded to S3: {key}")
            return filename
        except Exception as e:
            current_app.logger.error(f"Error uploading to S3: {e}")
            return None

    def get_file_url(self, memorial_id, filename):
        """Get the URL for a file"""
        if self.use_local:
            return url_for('static', 
                         filename=f'uploads/{memorial_id}/{filename}')
            
        url = f"https://{self.bucket}.s3.{os.environ.get('AWS_REGION', 'us-east-1')}.amazonaws.com/uploads/{memorial_id}/{filename}"
        return url

    def delete_file(self, memorial_id, filename):
        """Delete a file"""
        if self.use_local:
            file_path = os.path.join(current_app.static_folder, 
                                   'uploads', 
                                   str(memorial_id), 
                                   filename)
            try:
                os.remove(file_path)
                return True
            except OSError as e:
                current_app.logger.error(f"Error deleting local file: {e}")
                return False
                
        try:
            key = f'uploads/{memorial_id}/{filename}'
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            current_app.logger.error(f"Error deleting from S3: {e}")
            return False 