import sys

sys.path.insert(0, '/var/www/serverCatalog/site')

from recipes import app as application

application.secret_key = 'secret key error'

