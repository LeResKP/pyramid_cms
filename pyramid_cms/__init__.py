from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

# Add the modules you want to be include in the config
views_modules = [
    'pyramid_cms.views.view',
    'pyramid_cms.views.admin',
]

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    for module in views_modules:
        config.include(module)
    config.scan()
    return config.make_wsgi_app()

