import boto3
from django.conf import settings

UPLOADS_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False,
    )
