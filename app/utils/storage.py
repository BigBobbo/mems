import boto3
import os
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from flask import current_app, url_for

class S3Storage:
    def __init__(self):
        # Force S3 storage if running on Render
        self.use_local = (
            os.environ.get('USE_LOCAL_STORAGE') == 'True' and 
            not os.environ.get('RENDER')
        )
        
        if not self.use_local:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
            self.bucket = os.environ.get('AWS_BUCKET_NAME')
            
        # Create local upload directory for development
        if self.use_local:
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

    def upload_file(self, file_obj, memorial_id, filename):
        """Upload a file to S3 or local storage"""
        filename = secure_filename(filename)
        
        if self.use_local:
            # Save locally
            upload_dir = os.path.join(current_app.static_folder, 'uploads', str(memorial_id))
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file_obj.save(file_path)
            return filename
            
        try:
            key = f'uploads/{memorial_id}/{filename}'
            self.s3.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={
                    'ContentType': file_obj.content_type
                }
            )
            return filename
        except ClientError as e:
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