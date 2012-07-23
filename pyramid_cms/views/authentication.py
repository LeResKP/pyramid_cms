from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    )
from pyramid.security import (
    remember,
    forget,
    )

import tw2.forms as twf, tw2.core as twc
from urllib import urlencode

from .. import (
    security, 
    validators,
    )


class LoginForm(twf.TableForm):
    email = twf.TextField(validator=twc.EmailValidator(required=True))
    password = twf.PasswordField(validator=twc.Validator(required=True))
    
    validator = validators.UserExists(
                    login='email', 
                    password='password', 
                    validate_func=security.validate_password)


def login(context, request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'
    next = request.params.get('next', referrer)

    widget = LoginForm().req()
    if request.method == 'POST':
        try:
            data = widget.validate(request.POST)
            headers = remember(request, data['email'])
            return HTTPFound(location = next,
                             headers = headers)
        except twc.ValidationError, e:
            widget = e.widget

    return dict(
        widget=widget,
        )

def logout(context, request):
    headers = forget(request)
    location = request.params.get('next', request.application_url)
    return HTTPFound(location=location, headers=headers)

def forbidden(context, request):
    return {}

def forbidden_redirect(context, request):
    if request.user:
        # The user is logged but doesn't have the right permission
        location = request.route_url('forbidden')
    else:
        login_url = request.route_url('login')
        location = '%s?%s' % (login_url, urlencode({'next': request.url}))
    return HTTPFound(location=location)


def includeme(config):
    config.add_view(
        forbidden_redirect,
        context=HTTPForbidden,
        )

    config.add_route(
        'forbidden',
        '/forbidden', 
        view=forbidden,
        renderer='forbidden.mak',
        )

    config.add_route(
        'login',
        '/login', 
        view=login, 
        renderer='login.mak',
        )

    config.add_view(
        logout,
        name='logout',
        )
