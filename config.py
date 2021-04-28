import configparser

def api_key():
    return _api_key

def api_secret_key():
    return _api_secret_key

def access_token():
    return _access_token

def access_token_secret():
    return _access_token_secret

_config = configparser.ConfigParser()
_config.read('config.ini')

_api_key = _config['TwitterAPI']['api_key']
_api_secret_key = _config['TwitterAPI']['api_secret_key']
_access_token = _config['TwitterAPI']['access_token']
_access_token_secret = _config['TwitterAPI']['access_token_secret']