=============

url(r'^static\/(?P<path>.*)$','django.views.static.serve', {'document_root': settings.STATIC_ROOT })
[RemovedInDjango110Warning: Support for string view arguments to url() is deprecated and will be removed in Django 1.10 (got django.views.static.serve). Pass the callable instead.]
==>
from django.views.static import serve
url(r'^static\/(?P<path>.*)$',serve, {'document_root': settings.STATIC_ROOT })

=============
