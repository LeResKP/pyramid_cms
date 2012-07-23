import unittest
import transaction
from pyramid import testing

from .. import route
from ..models import (
    User,
    DBSession,
    Base,
    Page,
    )

class TestRoute(unittest.TestCase):

    def setUp(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            self.page = Page(name='root', url='/', content='Root page content')
            DBSession.add(self.page)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_get_url(self):
        info = {'match': {'url': ''}}
        url = route.get_url(info)
        self.assertEqual(url, '/')

        info = {'match': {'url': 'page1/'}}
        url = route.get_url(info)
        self.assertEqual(url, '/page1')

        info = {'match': {'url': 'page1'}}
        url = route.get_url(info)
        self.assertEqual(url, '/page1')

    def test_exist_page(self):
        info = {'match': {'url': 'page1/'}}
        self.assertFalse(route.exist_page(info, None))

        info = {'match': {'url': '/'}}
        self.assertTrue(route.exist_page(info, None))
        
    def test_factory(self):
        request = testing.DummyRequest()
        request.matchdict = {}
        self.assertFalse(route.factory(request))

        request.matchdict = {'pageobj': self.page}
        self.assertEqual(route.factory(request), self.page)

