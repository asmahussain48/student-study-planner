"""
Simple CLI helper to run project maintenance tasks such as testing the Generative AI API key.
Usage:
  python manage.py test-api

This script intentionally does not contain secrets. It loads environment variables via python-dotenv when present.
"""
import sys
from dotenv import load_dotenv
load_dotenv()

from ai import test_api_key

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python manage.py <command>')
        print('Commands: test-api')
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'test-api':
        result = test_api_key()
        import json
        print(json.dumps(result, indent=2))
    elif cmd == 'list-models':
        from ai import list_models
        key = None
        # Try reading env
        import os
        key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not key:
            print('GEMINI_API_KEY (or GOOGLE_API_KEY) not set in environment. Set it or pass via env before running this command.')
            sys.exit(1)
        ok, data = list_models(key)
        import json
        if ok:
            print('Available models:')
            print(json.dumps(data, indent=2))
        else:
            print('Failed to list models:')
            print(data)
            sys.exit(1)
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(2)
