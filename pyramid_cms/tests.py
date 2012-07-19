import unittest
import transaction

from pyramid import testing

from .models import DBSession

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            Page,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = Page(name='root', url='/', content='Root page content')
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        page = info['page']
        self.assertEqual(page.name, 'root')
        self.assertEqual(page.content, 'Root page content')
        self.assertEqual(info['project'], 'pyramid_cms')
