

from api.aws_s3.aws_s3_operations import check_if_object_exists_and_get_size
from api.exceptions import NotFoundException
from api.enumerations.upload_status_enum import UploadStatusEnum
from api.database.models import S3Object, UploadUrl
from api.database.db import db
from api.aws_s3.aws_s3_operations import UPLOAD_URL_EXPIRY

def add_new_upload_url(generated_upload_url_dict, current_user_id, s3_object_uuid,
  s3_object_extension, path_to_object, s3_bucket_name, object_type_id):
  new_upload_url = UploadUrl(
    generated_upload_url=generated_upload_url_dict.get('url'),
    status_id=UploadStatusEnum.REQUESTED.value,
    upload_url_expiry=UPLOAD_URL_EXPIRY,
    generated_for_user_id=current_user_id,
    s3_object_uuid=s3_object_uuid,
    s3_object_extension=s3_object_extension,
    path_to_object=path_to_object,
    s3_bucket_name=s3_bucket_name,
    object_type_id=object_type_id,
    x_amz_algorithm=generated_upload_url_dict['fields']['x-amz-algorithm'],
    x_amz_credential=generated_upload_url_dict['fields']['x-amz-credential'],
    x_amz_date=generated_upload_url_dict['fields']['x-amz-date'],
    policy=generated_upload_url_dict['fields']['policy'],
    x_amz_signature=generated_upload_url_dict['fields']['x-amz-signature']
  )
  db.session.add(new_upload_url)
  db.session.commit()
  return new_upload_url.id


def update_upload_url_status(upload_url_id, new_status_id, current_user_id):
  upload_url = UploadUrl.query.filter(
    UploadUrl.id == upload_url_id,
    UploadUrl.generated_for_user_id == current_user_id
  ).one_or_none()
  if upload_url is None:
    raise NotFoundException('Url Not Found!')
  object_full_key = upload_url.path_to_object + upload_url.s3_object_uuid + '.' + upload_url.s3_object_extension
  object_size = check_if_object_exists_and_get_size(object_full_key)
  upload_url.status_id = new_status_id
  s3_object = S3Object.load_from_upload_url(upload_url=upload_url, object_size=object_size)
  db.session.add(s3_object)
  db.session.commit()
