import boto3
from botocore.config import Config
from flask import current_app

def get_s3_client():
  return boto3.client(
    "s3",
    config=Config(signature_version='s3v4'),
    region_name="eu-west-1",
    aws_access_key_id=current_app.config['S3_KEY'],
    aws_secret_access_key=current_app.config['S3_SECRET']
  )

DOWNLOAD_URL_EXPIRY=24*60*60
UPLOAD_URL_EXPIRY=5*60

def generate_download_url(object_key):
  s3_client = get_s3_client()
  response = s3_client.generate_presigned_url('get_object',
                                            Params={
                                              'Bucket': current_app.config['S3_BUCKET'],
                                              'Key': object_key
                                            },
                                            ExpiresIn=DOWNLOAD_URL_EXPIRY)
  return response

def generate_upload_url(object_key):
  s3_client = get_s3_client()
  response = s3_client.generate_presigned_post(Bucket=current_app.config['S3_BUCKET'],
                                               Key=object_key,
                                               ExpiresIn=UPLOAD_URL_EXPIRY)
  print(f'Amazon s3 response => ' + str(response))
  return response            

def check_if_object_exists_and_get_size(object_key):
  s3_client = get_s3_client()
  print(f'object key to head : {object_key}')
  response = s3_client.head_object(Bucket=current_app.config['S3_BUCKET'], Key=object_key)
  print('head object response : ' + str(response))
  object_size = response['ContentLength']
  return object_size