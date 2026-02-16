#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    # Load BLOG_ENV_ID from settings/.env
    env_path = Path(__file__).resolve().parent / 'settings' / '.env'
    env_id = 'local'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('BLOG_ENV_ID='):
                    env_id = line.split('=')[1].strip()
                    break

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{env_id}')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()