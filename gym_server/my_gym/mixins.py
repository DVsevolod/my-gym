from django.http import HttpResponseNotFound

from .errors import RoleURLParamError


class CheckValidParamMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            role = int(request.GET.get('role', None))
        except TypeError:
            role = None
        if role != 1 and role != 2:
            return HttpResponseNotFound(RoleURLParamError.msg)
        else:
            return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)