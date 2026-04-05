from django.urls import path
from .views import list_users, get_user, update_user, delete_user
from .views import create_user, list_users, get_user, update_user, delete_user

urlpatterns = [
    path("", list_users, name="list_users"),
    path("<uuid:pk>/", get_user, name="get_user"),
     path('register/', create_user, name='create_user'),
    path("<uuid:pk>/update/", update_user, name="update_user"),
    path("<uuid:pk>/delete/", delete_user, name="delete_user"),
]
