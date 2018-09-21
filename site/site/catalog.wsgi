# def application(environ, start_response):
#     status = '200 OK'
#     output = index.html
#
#     response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)
#
#     return [output]

import sys
sys.path.append('/vagrant/serverCatalog/recipes.py')
from recipes import app as application
