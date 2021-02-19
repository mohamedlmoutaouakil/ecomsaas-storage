from datetime import datetime
from api.enumerations.object_type_enum import ObjectTypeEnum
from api.enumerations.upload_status_enum import UploadStatusEnum
from api.database.db import db

class S3Object(db.Model):
  __tablename__ = 's3_objects'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  s3_object_extension = db.Column(db.String(4))
  s3_object_uuid = db.Column(db.String(40), nullable=False)
  path_to_object = db.Column(db.String(128))
  s3_bucket_name = db.Column(db.String(63), nullable=False)
  owner_user_id = db.Column(db.Integer)
  object_type_id = db.Column(db.Integer, db.ForeignKey('object_types.id'),
    nullable=False)
  object_type = db.relationship('ObjectType', lazy=True)
  object_size_in_bytes = db.Column(db.Integer)
  upload_url_id = db.Column(db.Integer, db.ForeignKey('upload_urls.id'),
    nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  @classmethod
  def load_from_upload_url(cls, upload_url, object_size):
    s3_object = S3Object(
      s3_object_extension=upload_url.s3_object_extension,
      s3_object_uuid=upload_url.s3_object_uuid,
      path_to_object=upload_url.path_to_object,
      s3_bucket_name=upload_url.s3_bucket_name,
      owner_user_id=upload_url.generated_for_user_id,
      object_type_id=upload_url.object_type_id,
      upload_url_id=upload_url.id,
      object_size_in_bytes=object_size,
    )
    return s3_object

class AllowedToDownload(db.Model):
  __tablename__ = 'allowed_to_download'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  s3_object_id = db.Column(db.Integer, db.ForeignKey('s3_objects.id'),
    nullable=False)
  s3_object = db.relationship('S3Object', lazy=True)
  allowed_user_id = db.Column(db.Integer)
  allowed_user_type = db.Column(db.String(25))
  user_id_allowing = db.Column(db.Integer)
  user_type_allowing = db.Column(db.String(25))
  

class DownloadUrl(db.Model):
  __tablename__ = 'download_urls'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  generated_download_url = db.Column(db.String(2048))
  generated_at = db.Column(db.DateTime)
  download_url_expiry = db.Column(db.Integer)
  generated_for_user_id = db.Column(db.Integer)
  s3_object_id = db.Column(db.Integer, db.ForeignKey('s3_objects.id'),
    nullable=False)
  s3_object = db.relationship('S3Object', lazy=True)

class UploadUrl(db.Model):
  __tablename__ = 'upload_urls'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  generated_upload_url = db.Column(db.String(2048))
  status_id = db.Column(db.Integer, db.ForeignKey('upload_statuses.id'),
    nullable=False)
  status = db.relationship('UploadStatus', lazy=True)
  generated_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  upload_url_expiry = db.Column(db.Integer)
  generated_for_user_id = db.Column(db.Integer)
  s3_object_uuid = db.Column(db.String(32))
  s3_object_extension = db.Column(db.String(40), nullable=False)
  path_to_object = db.Column(db.String(128))
  s3_bucket_name = db.Column(db.String(63), nullable=False)
  object_type_id = db.Column(db.Integer, db.ForeignKey('object_types.id'),
    nullable=False)
  x_amz_algorithm = db.Column(db.String(128))
  x_amz_credential = db.Column(db.String(256))
  x_amz_date = db.Column(db.String(16))
  policy = db.Column(db.String(1000))
  x_amz_signature = db.Column(db.String(128))

class ObjectType(db.Model):
  __tablename__ = 'object_types'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  label = db.Column(db.String(50))

  def dump(self):
    return {
      'id': self.id,
      'label': self.label 
    }

class UploadStatus(db.Model):
  __tablename__  = 'upload_statuses'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  label = db.Column(db.String(15))

@db.event.listens_for(UploadStatus.__table__, 'after_create')
def initialize_statuses(*args, **kwargs):
  statuses = [status.name for status in list(UploadStatusEnum)]
  statuses_models = [UploadStatus(label=status_label) for status_label in statuses]
  db.session.bulk_save_objects(statuses_models)
  db.session.commit()

@db.event.listens_for(ObjectType.__table__, 'after_create')
def initialize_statuses(*args, **kwargs):
  object_types = [object_type.name for object_type in list(ObjectTypeEnum)]
  object_types_models = [ObjectType(label=type_label) for type_label in object_types]
  db.session.bulk_save_objects(object_types_models)
  db.session.commit()