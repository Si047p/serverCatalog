# def application(environ, start_response):
#     status = '200 OK'
#     output = index.html
#
#     response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)
#
#     return [output]

import sys
from recipes import app as application

application.secret_key = 'secret key error'
sys.path.insert(0, '/vagrant/serverCatalog/site')
