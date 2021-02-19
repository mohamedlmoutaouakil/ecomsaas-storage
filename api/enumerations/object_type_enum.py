from enum import Enum

class ObjectTypeEnum(Enum):
  PRODUCT_IMAGE = 1
  PACKAGE_IMAGE = 2
  CIN_IMAGE = 3
  USER_AVATAR = 4
  CONTRACT = 5

  @classmethod
  def has_value(cls, value):
    return value in cls._value2member_map_