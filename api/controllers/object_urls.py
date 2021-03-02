from api.aws_s3.aws_s3_operations import generate_download_url, generate_upload_url
from api.enumerations.object_type_enum import ObjectTypeEnum
from api.enumerations.upload_status_enum import UploadStatusEnum
from api.database.objects_info_dal import add_new_upload_url, update_upload_url_status
from api.enumerations.object_type_enum import ObjectTypeEnum
from botocore.exceptions import ClientError
from api.database.models import AllowedToDownload, ObjectType, S3Object
from flask.globals import current_app
from api.exceptions import BadRequestException, NotFoundException
import uuid

def get_download_url(object_id, token_info=None):
  try:
    current_user_id, current_user_type = token_info['sub'], token_info['roles'][0]
    if current_user_type not in ['admin', 'seller', 'call_center_agent'] :
      return 'Not Authorized!', 400
    object_in_db = None
    if current_user_type == 'seller':
      object_in_db = S3Object.query.filter(S3Object.id == object_id, S3Object.owner_user_id == current_user_id).one_or_none()
    elif current_user_type == 'call_center_agent':
      is_allowed = current_app.redis_client.exists(object_id + '|' + current_user_id + '|' + current_user_type)
      if not is_allowed:
        return 'Not Authorized!', 400
      object_in_db = S3Object.query.filter(S3Object.id == object_id).one_or_none()
    elif current_user_type == 'admin':
      object_in_db = S3Object.query.filter(S3Object.id == object_id).one_or_none()

    if object_in_db is None:
      return 'Document Not Found!', 404

    object_full_key = object_in_db.path_to_object + object_in_db.s3_object_uuid + '.' + object_in_db.s3_object_extension
    download_url = generate_download_url(object_full_key)
    return download_url
  except ClientError as e:
    return 'Internal Server Error', 500

def get_upload_url(extension, object_type, token_info=None):
  try:
    current_user_id, current_user_type = token_info['sub'], token_info['roles'][0]
    extension = extension.lower()
    if current_user_type not in ['admin', 'seller', 'call_center_agent', 'delivery_agent']:
      return 'Not Authorized!', 400
    if extension not in ['png', 'jpeg', 'jpg', 'pdf']:
      return 'Document extensions allowed are: jpg, jpeg, png, pdf', 400
    if not ObjectTypeEnum.has_value(object_type):
      return 'Invalid Document Type!', 400 
    
    object_type_enum = ObjectTypeEnum(object_type)
    _can_user_upload_object_type(user_type=current_user_type, object_type_enum=object_type_enum)
    _is_valid_object_type_and_extension(object_type_enum=object_type_enum, extension=extension)
    
    user_type_subfolder = current_user_type + 's'
    type_subfolder =  object_type_enum.name + 'S'
    object_uuid = str(uuid.uuid4())
    object_uuid_with_extension = object_uuid + '.' + extension
    path_to_object = 'users/' + user_type_subfolder + '/' + str(current_user_id) + '/' + type_subfolder + '/'
    object_full_key = path_to_object + object_uuid_with_extension

    print(f'Generate upload url for key : {object_full_key}')
    upload_url_dict = generate_upload_url(object_full_key)
    upload_url_id = add_new_upload_url(
      generated_upload_url_dict=upload_url_dict,
      current_user_id=current_user_id,
      s3_object_uuid=object_uuid,
      s3_object_extension=extension,
      path_to_object=path_to_object, 
      s3_bucket_name=current_app.config['S3_BUCKET'], 
      object_type_id=object_type
    )

    upload_url_dict['id'] = upload_url_id
    upload_url_dict['status'] = {
      'id': UploadStatusEnum.REQUESTED.value,
      'label': UploadStatusEnum.REQUESTED.name
    }

    return upload_url_dict
  except ClientError as e:
    return 'Internal Server Error', 500
  except BadRequestException as e:
    return str(e), 400
  except NotFoundException as e:
    return str(e), 404
  except Exception as e:
    return 'Internal Server Error', 500

def update_upload_url(id, body, token_info=None):
  try:
    current_user_id, current_user_type = token_info['sub'], token_info['roles'][0]
    if current_user_type not in ['admin', 'seller']:
      return 'Not Authorized!', 400

    update_upload_url_status(id, UploadStatusEnum.UPLOADED.value, current_user_id=current_user_id)
  except ClientError as e:
    return 'Not Yet Uploaded!', 400
  except Exception as e:
    return 'Internal Server Error!', 500

def _is_valid_object_type_and_extension(object_type_enum, extension):
  if extension == 'pdf' and object_type_enum != ObjectTypeEnum.CONTRACT:
    raise BadRequestException('Document type does not correspond to document extension!')
  if extension in ['jpg', 'jpeg', 'png'] and object_type_enum not in [ObjectTypeEnum.PRODUCT_IMAGE,
                                                                      ObjectTypeEnum.PACKAGE_IMAGE,
                                                                      ObjectTypeEnum.CIN_IMAGE,
                                                                      ObjectTypeEnum.USER_AVATAR]:
    raise BadRequestException('Document type does not correspond to document extension!')

def _can_user_upload_object_type(user_type, object_type_enum):
  if object_type_enum == ObjectTypeEnum.PRODUCT_IMAGE and user_type != 'seller':
    raise BadRequestException('Not Authorized!')
  if object_type_enum == ObjectTypeEnum.PACKAGE_IMAGE and user_type != 'delivery_agent':
    raise BadRequestException('Not Authorized!')
  