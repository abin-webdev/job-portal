from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def root(request):
    return redirect("login")   # Always go to login page first

urlpatterns = [
    path('', root), 
    path('', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)