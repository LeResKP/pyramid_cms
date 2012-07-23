import unittest
import transaction
from pyramid import testing

from ..views import authentication
from ..models import (
    User,
    DBSession,
    Base,
    Page,
    )


class TestAuthentification(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route(
            'login', 
            '/login',
            view=authentication.login, 
            renderer='login.mak',
            )
        self.config.add_route(
            'forbidden',
            '/forbidden', 
            view=authentication.forbidden,
            renderer='forbidden.mak',
            )
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            self.user1 = User(email='user1@lereskp.fr', password='pass1')
            DBSession.add(self.user1)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_login(self):
        request = testing.DummyRequest()
        response = authentication.login(None, request)
        self.assertEqual(len(response), 1)
        assert('widget' in response)

    def test_login_invalid_post(self):
        request = testing.DummyRequest(post={'email': 'user1@lereskp.fr',
                                             'password': 'invalid'})
        response = authentication.login(None, request)
        self.assertEqual(len(response), 1)
        assert('widget' in response)

    def test_login_empty_post(self):
        request = testing.DummyRequest(post={})
        response = authentication.login(None, request)
        self.assertEqual(len(response), 1)
        assert('widget' in response)
        
    def test_login_post(self):
        request = testing.DummyRequest(post={'email': 'user1@lereskp.fr',
                                             'password': 'pass1'})
        response = authentication.login(None, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com') in response._headerlist)

        request = testing.DummyRequest(post={'email': 'user1@lereskp.fr',
                                             'password': 'pass1'},
                                       params={'next': 'http://example.com/next-page'})
        response = authentication.login(None, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com/next-page') in response._headerlist)

    def test_logout(self):
        request = testing.DummyRequest()
        response = authentication.logout(None, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com') in response._headerlist)

    def test_forbidden(self):
        request = testing.DummyRequest()
        response = authentication.forbidden(None, request)
        self.assertEqual(response, {})

    def test_forbidden_redirect(self):
        request = testing.DummyRequest()
        request.user = None
        response = authentication.forbidden_redirect(None, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com/login?next=http%3A%2F%2Fexample.com') in response._headerlist)

        request.user = 'Fake user'
        response = authentication.forbidden_redirect(None, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com/forbidden') in response._headerlist)


class FunctionalTests(unittest.TestCase):

    viewer_login = '/login'
    viewer_logout = '/logout'
    viewer_forbidden = '/forbidden'
    viewer_edit = '/edit'

    def setUp(self):
        from pyramid_cms import main
        import tw2.core as twc
        settings = {'sqlalchemy.url': 'sqlite://',
                    'authentication.key': 'secret',
                    'authentication.debug': True,
                    'mako.directories': 'pyramid_cms:templates',
                   }
        app = main({}, **settings)
        app = twc.middleware.TwMiddleware(app)
        from webtest import TestApp
        self.testapp = TestApp(app)
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            self.user1 = User(email='user1@lereskp.fr', password='pass1')
            page = Page(name='root', url='/', content='Root page content')
            DBSession.add(self.user1)
            DBSession.add(page)

    def tearDown(self):
        del self.testapp
        DBSession.remove()

    def test_login(self):
        response = self.testapp.get(self.viewer_login, status=200)
        self.assertTrue('Login Page' in response.body)

    def test_login_invalid_post(self):
        response = self.testapp.post(self.viewer_login, params={'email': 'user1@lereskp.fr', 'password': 'invalid'}, status=200)
        self.assertTrue('Login Page' in response.body)
        self.assertTrue('<input name="email" type="text" id="email" value="user1@lereskp.fr"/>' in response.body)
        self.assertTrue('Please check your posted data.' in response.body)

    def test_login_post(self):
        response = self.testapp.post(self.viewer_login, params={'email': 'user1@lereskp.fr', 'password': 'pass1'}, status=302)
        self.assertTrue(('Location', 'http://localhost/') in response._headerlist)
        self.assertTrue([key for key, value in response._headerlist if key == 'Set-Cookie'])

    def test_logout(self):
        response = self.testapp.get(self.viewer_logout, status=302)
        self.assertTrue(('Location', 'http://localhost') in response._headerlist)
        self.assertTrue([key for key, value in response._headerlist if key == 'Set-Cookie'])

    def test_forbidden(self):
        response = self.testapp.get(self.viewer_forbidden, status=200)
        self.assertTrue('You don\'t have the right permissions' in response.body)

    def test_forbidden_redirect(self):
        response = self.testapp.get(self.viewer_edit, status=302)
        self.assertTrue(('Location', 'http://localhost/login?next=http%3A%2F%2Flocalhost%2Fedit') in response._headerlist)
        response = self.testapp.post(self.viewer_login, params={'email': 'user1@lereskp.fr', 'password': 'pass1'})
        response = self.testapp.get(self.viewer_edit, status=302)
        self.assertTrue(('Location', 'http://localhost/forbidden') in response._headerlist)
