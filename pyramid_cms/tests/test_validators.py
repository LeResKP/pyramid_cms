import unittest
import transaction
from pyramid import testing

import tw2.core as twc
from .. import security
from .. import validators
from ..models import (
    User,
    DBSession,
    Base,
    )


class TestValidators(unittest.TestCase):

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

    def test_UserExists(self):
        validator = validators.UserExists(login='email', password='password', validate_func=security.validate_password)
        values = dict(
            email='nonexisting@lereskp.fr',
            password='admin'
            )
        self.assertRaises(twc.ValidationError, validator.validate_python, values, None)

        values = dict(
            email='user1@lereskp.fr',
            password='Pass1'
            )
        self.assertRaises(twc.ValidationError, validator.validate_python, values, None)

        values = dict(
            email='user1@lereskp.fr',
            password='pass1'
            )
        self.assertEqual(validator.validate_python(values, None), None)

