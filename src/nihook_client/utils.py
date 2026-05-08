import os

NOCODB_HOST = os.getenv('NOCODB_HOST', 'http://localhost')
NOCODB_TOKEN = os.getenv('NOCODB_TOKEN', 'none')
NOCODB_SSL_CERT = os.getenv('NOCODB_SSL_CERT', "True").lower() in ('true', '1', 't') # optional
