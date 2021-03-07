from flask import current_app
import jwt
from werkzeug.exceptions import Unauthorized
from flask import current_app
import requests
from base64 import b64decode

def get_jwks():
  AUTH_SERVICE_URL = 'http://localhost:5000'
  JWKS_ENDPOINT = '/.well-known/jwks.json'
  
  if_none_match = '0'
  if current_app.redis_client.exists("users_service.last_pubkey_version"):
    if_none_match = current_app.redis_client.get("users_service.last_pubkey_version")

  resp = requests.get(current_app.config['AUTH_SERVICE_URL'] + JWKS_ENDPOINT, headers={'If-None-Match' : if_none_match})
  if resp.status_code not in [200, 304]:
    raise Exception('Error getting public key from authentication service')
  if resp.status_code == 200:
    json_resp = resp.json()
    current_app.redis_client.set('users_service.pubkey', b64decode(json_resp['n'].encode('utf-8')))
    current_app.redis_client.set('users_service.last_pubkey_version', resp.headers['etag'])
  pubkey = current_app.redis_client.get('users_service.pubkey')
  return pubkey


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
      key = get_jwks()
      payload = jwt.decode(auth_token, key, algorithms=['RS512'])
      is_token_blacklisted = current_app.redis_client.exists(auth_token)
      if is_token_blacklisted:
        raise jwt.InvalidTokenError
      return payload
    except jwt.ExpiredSignatureError:
      raise Unauthorized('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
      raise Unauthorized('Invalid token. Please log in again.')

def token_handler_for_connexion(auth_token):
  payload = decode_auth_token(auth_token)
  # I only found this way to do, if there is another way go ahead!
  payload_with_token = {
    "auth_token": auth_token,
    **payload
  }
  print('authenticated external user : ' + str(payload['sub']))
  return payload_with_token