from .models import DBSession, Page
import logging
from . import security

log = logging.getLogger(__name__)


def get_url(info):
    """Returns the url to use to find the Page object
    """
    url = info['match']['url']
    if url and url.endswith('/'):
        # remove the '/' at the end
        url = url[:-1]
    url = '/' + url
    log.debug('get_url: url: %s' % url)
    return url

def exist_page(info, request):
    url = get_url(info)
    pageobj = DBSession.query(Page).filter_by(url=url).first()
    if not pageobj:
        log.debug('exist_page: Page not found for url: %s' % url)
        return False
    # To avoid many query add the Page object in the info dict
    info['match']['pageobj'] = pageobj
    log.debug('exist_page: Page found for url: %s' % url)
    return True

def factory(request):
    # The pageobj is defined when we check that the page is existing when we try to find a route
    pageobj = request.matchdict.get('pageobj')
    if pageobj:
        log.debug('factory: Page object defined in the matchdic')
        security.set_object_permissions(pageobj)
        return pageobj

