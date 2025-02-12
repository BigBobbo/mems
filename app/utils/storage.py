import boto3
import os
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from flask import current_app

class S3Storage:
    def __init__(self):
        print("Initializing S3Storage with:")
        print(f"Access Key ID: {'*' * len(os.environ.get('AWS_ACCESS_KEY_ID', ''))}") 
        print(f"Bucket: {os.environ.get('AWS_BUCKET_NAME')}")
        print(f"Region: {os.environ.get('AWS_REGION', 'us-east-1')}")
        
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket = os.environ.get('AWS_BUCKET_NAME')

    def upload_file(self, file_obj, memorial_id, filename):
        """Upload a file to S3"""
        try:
            filename = secure_filename(filename)
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
        url = f"https://{self.bucket}.s3.{os.environ.get('AWS_REGION', 'us-east-1')}.amazonaws.com/uploads/{memorial_id}/{filename}"
        print(f"Generated S3 URL: {url}")  # Debug print
        return url

    def delete_file(self, memorial_id, filename):
        """Delete a file from S3"""
        try:
            key = f'uploads/{memorial_id}/{filename}'
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            current_app.logger.error(f"Error deleting from S3: {e}")
            return False 