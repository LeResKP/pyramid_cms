import unittest
import transaction

from pyramid import testing

from ..models import (
    DBSession,
    Base,
    Page,
    User,
    Role,
    )
from ..views.admin import edit, add

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route('index', '/{url:.*}')
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            page = Page(name='root', url='/', content='Root page content')
            subpage = Page(name='subpage', url='/subpage', content='Subpage content')
            DBSession.add(page)
            DBSession.add(subpage)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_view(self):
        from ..views.view import index
        request = testing.DummyRequest()
        page = DBSession.query(Page).first()
        response = index(page, request)
        page = response['page']
        self.assertEqual(page.name, 'root')
        self.assertEqual(page.content, 'Root page content')
        self.assertEqual(response['project'], 'pyramid_cms')

    def test_admin_edit(self):
        request = testing.DummyRequest()
        page = DBSession.query(Page).first()
        response = edit(page, request)
        page = response['page']
        self.assertEqual(page.name, 'root')
        self.assertEqual(page.content, 'Root page content')
        widget = response['widget']
        self.assertEqual(widget.entity, page.__class__)
        self.assertEqual(widget.value, page)

    def test_admin_post_edit(self):
        request = testing.DummyRequest(post={'page_type': 'page', 
                                             'name': 'root', 
                                             'url': '/', 
                                             'content': 'Root page content updated'})
        page = DBSession.query(Page).first()
        response = edit(page, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com/') in response._headerlist)
        page = DBSession.query(Page).first()
        self.assertEqual(page.name, 'root')
        self.assertEqual(page.content, 'Root page content updated')

        request = testing.DummyRequest(post={'page_type': 'page', 
                                             'name': 'subpage',
                                             'url': '/subpage',
                                             'content': 'Subpage content updated'})
        page = DBSession.query(Page).filter_by(name='subpage').one()
        response = edit(page, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com/subpage') in response._headerlist)
        page = DBSession.query(Page).filter_by(name='subpage').one()
        self.assertEqual(page.name, 'subpage')
        self.assertEqual(page.content, 'Subpage content updated')

    def test_admin_invalid_post_edit(self):
        request = testing.DummyRequest(post={'page_type': 'page', 
                                             'name': '',
                                             'url': '/', 
                                             'content': 'Root page content updated'})
        page = DBSession.query(Page).first()
        response = edit(page, request)
        page = response['page']
        self.assertEqual(page.name, 'root')
        self.assertEqual(page.content, 'Root page content')
        widget = response['widget']
        self.assertEqual(widget.entity, page.__class__)
        self.assertEqual(widget.value, None)
        self.assertEqual(widget._validated, True)

    def test_admin_add(self):
        request = testing.DummyRequest()
        page = DBSession.query(Page).first()
        response = add(page, request)
        widget = response['widget']
        self.assertEqual(widget.entity, Page)
        self.assertEqual(widget.value, None)

    def test_admin_post_add(self):
        request = testing.DummyRequest(post={'page_type': 'page',
                                             'name': 'newpage', 
                                             'url': '/newpage', 
                                             'content': 'New page content'})
        root_page = DBSession.query(Page).first()
        response = add(root_page, request)
        self.assertEqual(response._status, '302 Found')
        assert(('Location', 'http://example.com/newpage') in response._headerlist)
        page = DBSession.query(Page).filter_by(name='newpage').one()
        root_page = DBSession.query(Page).first()
        self.assertEqual(page.content, 'New page content')
        self.assertEqual(page.parent, root_page)

    def test_admin_invalid_post_add(self):
        request = testing.DummyRequest(post={'page_type': 'page', 
                                             'name': '',
                                             'url': '/', 
                                             'content': 'Root page content updated'})
        page = DBSession.query(Page).first()
        response = add(page, request)
        widget = response['widget']
        self.assertEqual(widget.entity, page.__class__)
        self.assertEqual(widget.value, None)
        self.assertEqual(widget._validated, True)


class FunctionalTests(unittest.TestCase):

    viewer_view = '/'
    viewer_edit = '/edit'
    viewer_login = '/login'

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
            self.role = Role(name='admin')
            page = Page(name='root', url='/', content='Root page content')
            DBSession.add(self.user1)
            DBSession.add(self.role)
            DBSession.add(page)

    def tearDown(self):
        del self.testapp
        DBSession.remove()

    def test_view(self):
        response = self.testapp.get(self.viewer_view, status=200)
        self.assertTrue('Root page content' in response.body)

    def test_edit(self):
        response = self.testapp.get(self.viewer_edit, status=302)
        self.assertTrue(('Location', 'http://localhost/login?next=http%3A%2F%2Flocalhost%2Fedit') in response._headerlist)

        response = self.testapp.post(self.viewer_login, params={'email': 'user1@lereskp.fr', 'password': 'pass1'})
        response = self.testapp.get(self.viewer_edit, status=302)
        self.assertTrue(('Location', 'http://localhost/forbidden') in response._headerlist)
        DBSession.add(self.user1)
        DBSession.add(self.role)
        self.user1.roles = [self.role]
        response = self.testapp.get(self.viewer_edit, status=200)
        self.assertTrue('<form enctype="multipart/form-data" method="post">' in response.body)

