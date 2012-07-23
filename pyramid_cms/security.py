from pyramid.security import unauthenticated_userid, Everyone, Allow
import sqlalchemy.orm.exc as sqla_exc
import logging

from .models import User

log = logging.getLogger(__name__)

def get_user(userid):
    if not userid:
        return None
    try:
        return User.query.filter_by(email=userid).one()
    except sqla_exc.NoResultFound:
        pass
    except sqla_exc.MultipleResultsFound, e:
        log.exception(e)

def get_user_from_request(request):
    userid = unauthenticated_userid(request)
    return get_user(userid)

def validate_password(userid, password):
    user = get_user(userid)
    if not user:
        return False
    return user.password == password

def get_user_permissions(userid, request):
    user = get_user(userid)
    if not user:
        return []
    permissions = ['role:%s' % role.name for role in user.roles]
    permissions += ['group:%s' % group.name for group in user.groups]
    return permissions

def set_object_permissions(obj):
    obj.__acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'role:admin', 'edit'),
        (Allow, 'role:fakeadmin', 'add'),
    ]
