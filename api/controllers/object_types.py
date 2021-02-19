from api.database.models import ObjectType

def get():
  object_types = ObjectType.query.all()
  return [object_type.dump() for object_type in object_types]