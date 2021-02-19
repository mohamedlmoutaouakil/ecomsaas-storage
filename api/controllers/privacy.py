from api.database.models import AllowedToDownload, S3Object
from api.exceptions import BadRequestException, NotFoundException
from api.database.db import db

current_user_id, current_user_type = 5, 'call_center_service'

def grant_download_url(allowed_to_download):
  try:   
    if current_user_type not in ['admin', 'call_center_service']:
      raise BadRequestException('Not Authorized!')
    object_id = allowed_to_download.get('object_id')
    user_id = allowed_to_download.get('allowed_user_id')
    user_type = allowed_to_download.get('allowed_user_type')
    s3_object = S3Object.query.filter(
      S3Object.id == object_id
    ).one_or_none()
    if s3_object is None:
      raise NotFoundException('Document Not Found!')
    download_allownace = AllowedToDownload(
      s3_object_id=object_id,
      allowed_user_id=user_id,
      allowed_user_type=user_type,
      user_id_allowing=current_user_id,
      user_type_allowing=current_user_type
    )
    db.session.add(download_allownace)
    db.session.commit()
  except BadRequestException as e:
    return str(e), 400
  except NotFoundException as e:
    return str(e), 404
  except Exception as e:
    return 'Internal Server Error', 500