import os
import sys

path = '/home/pethostel/pethostel'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pet.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
