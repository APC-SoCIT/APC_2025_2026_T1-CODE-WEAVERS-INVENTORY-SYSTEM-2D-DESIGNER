"""
WSGI config for ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import tempfile
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Use Vercel settings when deployed on Vercel
if os.environ.get('VERCEL'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.vercel_settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# On Vercel cold start, ensure the SQLite DB temp directory exists and run migrations.
if os.environ.get('VERCEL'):
    try:
        temp_dir = Path(tempfile.gettempdir())
        temp_dir.mkdir(parents=True, exist_ok=True)
        flag_path = temp_dir / '.migrated'
        import django
        django.setup()
        from django.core.management import call_command

        # Optional: reset the database on boot if explicitly requested
        if os.getenv('RESET_DB_ON_BOOT', '') == '1':
            try:
                # Wipe data then re-apply migrations
                call_command('flush', interactive=False)
            except Exception as e:
                import sys
                print(f"[WSGI] Flush step failed: {e}", file=sys.stderr)
            try:
                call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
            except Exception as e:
                import sys
                print(f"[WSGI] Migrate after flush failed: {e}", file=sys.stderr)
            flag_path.touch()
        elif not flag_path.exists():
            # Create DB and apply migrations non-interactively
            call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
            flag_path.touch()
    except Exception as e:
        # Log but continue to let Django handle and surface the error in logs
        import sys
        print(f"[WSGI] Migration step failed: {e}", file=sys.stderr)

# Create WSGI application with verbose error logging to Vercel console
try:
    application = get_wsgi_application()
except Exception as e:
    # Surface full traceback to stderr so Vercel shows details
    import sys, traceback
    print(f"[WSGI] Application init failed: {e}", file=sys.stderr)
    traceback.print_exc()
    raise

# Expose 'app' alias for Vercel's Python runtime
app = application
