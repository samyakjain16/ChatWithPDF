from boto3 import client
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import settings
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.bucket_name = settings.AWS_BUCKET_NAME
        try:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY,
                region_name=settings.AWS_REGION
            )
            # Verify credentials and bucket access
            self.verify_setup()
        except Exception as e:
            logger.error(f"Failed to initialize S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="S3 configuration error. Please check your credentials."
            )

    def verify_setup(self):
        """Verify S3 credentials and bucket access"""
        try:
            # Try to access the bucket
            self.s3.head_bucket(Bucket=self.bucket_name)
            print(self.s3.head_bucket(Bucket=self.bucket_name))
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403':
                raise HTTPException(
                    status_code=500,
                    detail="Access denied to S3 bucket. Check your permissions."
                )
            elif error_code == '404':
                raise HTTPException(
                    status_code=500,
                    detail=f"S3 bucket {self.bucket_name} does not exist."
                )
            raise HTTPException(
                status_code=500,
                detail=f"S3 error: {str(e)}"
            )
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="AWS credentials not found."
            )

    async def upload_file(self, file, filename: str):
        """Upload a file to S3"""
        try:
            self.s3.upload_fileobj(
                file,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': 'application/pdf'}
            )
            return self.generate_presigned_url(filename)
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )

    def generate_presigned_url(self, key: str, expiration=3600):
        """Generate a presigned URL for file access"""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate file access URL"
            )

    async def list_files(self):
        """List all PDF files in the bucket"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='',  # List all files
            )
            files = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.pdf'):
                    files.append({
                        'key': obj['Key'],
                        'last_modified': obj['LastModified'],
                        'size': obj['Size'],
                        'url': self.generate_presigned_url(obj['Key'])
                    })
            return files
        except ClientError as e:
            logger.error(f"Failed to list files from S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to list files"
            )
