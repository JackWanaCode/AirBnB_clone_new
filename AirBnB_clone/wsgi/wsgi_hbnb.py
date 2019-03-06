#!/usr/bin/python3
"""
imports Flask instance for gunicorn configurations
gunicorn --bind 127.0.0.1:8003 wsgi.wsgi_hbnb:web_flask.app
"""

from web_dynamic.main_routes import app as application
#application = __import__('web_dynamic.main_routes',
#                       globals(), locals(), ['*'])

if __name__ == "__main__":
    """runs the main flask app"""
    application.run()
