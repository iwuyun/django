import os
import django
from django.conf import LazySettings, settings
from django.core.handlers.wsgi import WSGIHandler


def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Should return a WSGI
    callable.

    Allows us to avoid making django.core.handlers.WSGIHandler public API, in
    case the internal WSGI implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    return WSGIHandler()


class MultiSiteApplication():
    def __init__(self, module_map):
        for site, settings_module in module_map.iteritems():
            os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
            site_settings = LazySettings()
            site_settings._setup()
            settings.add_settings(site, site_settings)
        self._application = get_wsgi_application()

    def get_request_site(self, environ):
        return environ['SERVER_NAME']

    def __call__(self, environ, start_response):
        site = self.get_request_site(environ)
        settings.switch_settings(site)
        return self._application(environ, start_response)
