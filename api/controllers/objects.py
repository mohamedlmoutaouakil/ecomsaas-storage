from api.exceptions import BadRequestException, NotFoundException
from api.database.objects_info_dal import get_s3_object_info_by_id

def get_object_by_id(object_id, token_info=None):
  try:
    current_user_id, current_user_type = token_info['sub'], token_info['roles'][0]
    s3_object = get_s3_object_info_by_id(object_id, current_user_id, current_user_type)
    return s3_object, 200
  except BadRequestException as e:
    return str(e), 400
  except NotFoundException as e:
    return str(e), 404
  except Exception as e:
    return 'Internal Server Error', 500 