import tw2.core as twc, tw2.sqla as tws
import transaction

from pyramid.httpexceptions import (
    HTTPFound,
    )

from pyramid_cms import route
from ..models import DBSession, Page


def edit(context, request):
    widget = Page.getAdminForm().req()
    if request.method == 'POST':
        try:
            data = widget.validate(request.POST)
            data[context._pk_name] = context.id
            pageobj = tws.utils.update_or_create(widget.entity, data)
            transaction.commit()
            DBSession.add(pageobj) # Make sure object is bound to the session
            return HTTPFound(location = request.route_url('index',
                                                          url=pageobj.url[1:]))
        except twc.ValidationError, e:
            widget = e.widget
    else:
        widget.value = context
    return {'page':context, 'widget':widget, 'project':'pyramid_cms'}

def add(context, request):
    widget = Page.getAdminForm().req()
    if request.method == 'POST':
        try:
            data = widget.validate(request.POST)
            pageobj = tws.utils.update_or_create(widget.entity, data)
            pageobj.parent = context
            transaction.commit()
            DBSession.add(pageobj) # Make sure object is bound to the session
            return HTTPFound(location = request.route_url('index',
                                                          url=pageobj.url[1:]))
        except twc.ValidationError, e:
            widget = e.widget
    return {'page':context, 'widget':widget, 'project':'pyramid_cms'}


def includeme(config):
    config.add_route(
            'edit',
            '/{url:(.+/)?}edit',
            view=edit, 
            renderer='admin.mak',
            custom_predicates=(route.exist_page,),
            factory=route.factory,
            )
    config.add_route(
            'new',
            '/{url:(.+/)?}add',
            view=add, 
            renderer='admin.mak',
            custom_predicates=(route.exist_page,),
            factory=route.factory,
            )
