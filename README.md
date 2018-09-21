Project Title


Getting Started
The working version of the catalog can be accessed by visiting http://18.215.253.166.xip.io
The server can be accessed via ssh at ip address 18.215.253.166

Software Installed

Flask==0.12.2
Flask-HTTPAuth==3.2.3
Flask-SQLAlchemy==2.3.2
oauth2client==4.1.2
packaging==17.1
psycopg2-binary==2.7.4
SQLAlchemy==1.2.4
libapache2-mod-wsgi-py3
postgresql
apache2
finger

Completed Configurations
AWS server created
2 sudo users added (Grader,Sydney)
Remote root user access removed
Firewall activated from both the server and the AWS console.
Key based SSH created for remote SSH access.
Applications updated via apt-get.
Web and SSH ports updated.
postgresql install and catalog database setup with user catalog.
WSGI server created and 000-default.conf file updated to serve wsgi file within serverCatalog.
catalog.wsgi created to properly run server catalog on request.

Resources and Acknowledgments
https://www.compose.com/articles/using-postgresql-through-sqlalchemy/
https://www.jakowicz.com/flask-apache-wsgi/
https://stackoverflow.com/questions/6454564/target-wsgi-script-cannot-be-loaded-as-python-module
