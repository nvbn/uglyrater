from base import *
try:
    from local import *
except ImportError:
    print 'Create local.py!'
