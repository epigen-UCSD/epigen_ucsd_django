from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile
from django.core.exceptions import PermissionDenied
from .shared import is_member
 
EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
 
class LoginRequiredMiddleware(object):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).
    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE setting to insert\
 'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(settings.LOGIN_URL)
        return self.get_response(request)

INTERNAL_EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'INTERNAL_EXEMPT_URLS'):
    INTERNAL_EXEMPT_URLS += [compile(expr) for expr in settings.INTERNAL_EXEMPT_URLS]

class InternalRequiredMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        assert hasattr(request, 'user')
        #print(request.user)
        #print(is_member(request.user,'epigencollaborators'))
        if is_member(request.user,'epigencollaborators'):
            path = request.path_info.lstrip('/')
            print(path)
            if not any(m.match(path) for m in INTERNAL_EXEMPT_URLS):
                raise PermissionDenied
        return self.get_response(request)