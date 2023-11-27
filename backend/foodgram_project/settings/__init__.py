import os

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include('base.py')

DEBUG = os.getenv('DEBUG')
if DEBUG == 'True':
    include('develop.py')
elif DEBUG == 'False':
    include('production.py')
