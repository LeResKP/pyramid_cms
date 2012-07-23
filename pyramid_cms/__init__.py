from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import DBSession
from .security import get_user_permissions, get_user_from_request

# Add the modules you want to be include in the config
views_modules = [
    'pyramid_cms.views.view',
    'pyramid_cms.views.admin',
    'pyramid_cms.views.authentication',
]

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)

    authentication_policy = AuthTktAuthenticationPolicy(
        settings['authentication.key'], 
        callback=get_user_permissions, 
        debug=settings['authentication.debug']
        )
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    config.set_request_property(get_user_from_request, 'user', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    for module in views_modules:
        config.include(module)
    config.scan()
    return config.make_wsgi_app()

