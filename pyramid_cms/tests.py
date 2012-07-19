import unittest
import transaction

from pyramid import testing

from .models import (
    DBSession,
    Base,
    Page,
    )
from .views.admin import edit, add

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
        from .views.view import index
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
