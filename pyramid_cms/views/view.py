from pyramid_cms import route


def index(context, request):
    return {'page':context, 'project':'pyramid_cms'}

def includeme(config):
    config.add_route(
            'index',
            '/{url:.*}', 
            view=index, 
            renderer='index.mak',
            custom_predicates=(route.exist_page,),
            factory=route.factory,
            )
