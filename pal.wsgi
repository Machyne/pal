activate_this = '/var/www/pal/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from server import app as application
