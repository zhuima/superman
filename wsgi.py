import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from superman import create_app  # noqa

application = create_app('production')

if __name__ == '__main__':
    application.run()
