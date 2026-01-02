from django.urls import path, include
from django.shortcuts import redirect

def root(request):
    return redirect("login")   # Always go to login page first

urlpatterns = [
    path('', root), 
    path('', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    
]

