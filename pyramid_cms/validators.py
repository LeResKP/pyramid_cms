import tw2.core as twc


class UserExists(twc.Validator):
    """Validate the user exists in the DB. It's used when we want to
    authentificate it.
    """
    __unpackargs__ = ('login', 'password', 'validate_func')
    msgs = {
        'mismatch': 'Please check your posted data.',
    }

    def validate_python(self, value, state):
        super(UserExists, self).validate_python(value, state)
        login = value[self.login]
        password = value[self.password]
        for v in [login, password]:
            try:
                if issubclass(v, twc.validation.Invalid):
                    # No need to validate the password of the user, the login
                    # or password are invalid
                    return 
            except TypeError:
                pass

        if not self.validate_func(login, password):
            raise twc.ValidationError('mismatch', self)
