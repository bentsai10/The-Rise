import os
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
    custom_domain = '/{}.s3.{}.amazonaws.com/'.format(os.environ['AWS_STORAGE_BUCKET_NAME'], os.environ['AWS_BUCKET_REGION'])

class MediaStorage(S3Boto3Storage):
    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
    custom_domain = '/{}.s3.{}.amazonaws.com/'.format(os.environ['AWS_STORAGE_BUCKET_NAME'], os.environ['AWS_BUCKET_REGION'])