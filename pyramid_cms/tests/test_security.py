import unittest
import transaction
from pyramid import testing

from .. import security
from ..models import (
    User,
    Role,
    Group,
    DBSession,
    Base,
    Page,
    )

import logging

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class TestSecurity(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
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

    def test_get_user(self):
        assert(security.get_user('user1@lereskp.fr'))
        self.assertEqual(security.get_user('nonexisting@lereskp.fr'), None)
        
    def test_get_user_logging(self):
        handler = MockLoggingHandler()
        logging.getLogger().addHandler(handler)
        user = User(email='user1@lereskp.fr', password='pass1')
        DBSession.add(user)
        self.assertEqual(security.get_user('user1@lereskp.fr'), None)
        self.assertEqual(handler.messages['error'], ['Multiple rows were found for one()'])
    
    def test_get_user_from_request(self):
        request = testing.DummyRequest()
        self.assertEqual(security.get_user_from_request(request), None)
        self.config.testing_securitypolicy(userid='user1@lereskp.fr',
                                           permissive=False)
        assert(security.get_user_from_request(request))
        self.config.testing_securitypolicy(userid='nonexisting@lereskp.fr',
                                           permissive=False)
        self.assertEqual(security.get_user_from_request(request), None)

    def test_validate_password(self):
        self.assertEqual(security.validate_password('nonexisting@lereskp.fr', ''), False)
        self.assertEqual(security.validate_password('user1@lereskp.fr', ''), False)
        self.assertEqual(security.validate_password('user1@lereskp.fr', 'pass1'), True)

    def test_get_user_permissions(self):
        request = testing.DummyRequest()
        self.assertEqual(security.get_user_permissions('nonexisting@lereskp.fr', request), [])
        self.assertEqual(security.get_user_permissions('user1@lereskp.fr', request), [])
        DBSession.add(self.user1)
        role = Role(name='admin')
        self.user1.roles = [role]
        expected = ['role:admin']
        self.assertEqual(security.get_user_permissions('user1@lereskp.fr', request), expected)

        group = Group(name='group1')
        self.user1.groups = [group]
        expected = ['role:admin', 'group:group1']
        self.assertEqual(security.get_user_permissions('user1@lereskp.fr', request), expected)
    
    def test_set_object_permissions(self):
        page = Page()
        assert(not hasattr(page, '__acl__'))
        security.set_object_permissions(page)
        assert(type(page.__acl__) == list)


