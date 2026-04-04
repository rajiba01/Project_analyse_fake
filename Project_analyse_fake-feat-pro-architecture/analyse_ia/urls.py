from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api_root(request):
    return Response({
        "message": "API Authentication fonctionne !",
        "endpoints": {
            "register": "/api/auth/register/",
            "login": "/api/auth/login/",
            "profile": "/api/auth/profile/",
            "users": "/api/users/",
        }
    })


urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/users/", include("apps.users.urls")),
]