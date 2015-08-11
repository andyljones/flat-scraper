import os
import sys
import logging

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
