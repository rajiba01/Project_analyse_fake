from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analyse_ia.settings.development')

application = get_asgi_application()
